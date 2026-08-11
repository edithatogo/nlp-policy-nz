import concurrent.futures
import math

import nlp_policy_nz.api.metrics as metrics_mod
from nlp_policy_nz.api.metrics import (
    _ERROR_COUNTS,
    _REQUEST_COUNTS,
    _REQUEST_DURATION_COUNT,
    _REQUEST_DURATION_SUM,
    _REQUEST_HISTOGRAM,
    _render_labels,
    decrement_active_requests,
    increment_active_requests,
    record_request,
    render_metrics,
    reset_metrics,
    set_model_loaded,
)


def test_reset_metrics():
    # Setup some state
    increment_active_requests()
    set_model_loaded(True)
    record_request(method="GET", endpoint="/test", status=200, scope="public", duration_seconds=0.1)
    record_request(
        method="POST", endpoint="/error", status=500, scope="private", duration_seconds=1.5
    )

    # Assert state is mutated (checking via the module dict values since variables are primitive module level ints)
    assert metrics_mod._ACTIVE_REQUESTS > 0
    assert metrics_mod._MODEL_LOADED == 1
    assert len(_REQUEST_COUNTS) > 0
    assert len(_ERROR_COUNTS) > 0
    assert len(_REQUEST_DURATION_COUNT) > 0
    assert len(_REQUEST_DURATION_SUM) > 0
    assert len(_REQUEST_HISTOGRAM) > 0

    # Reset
    reset_metrics()

    # Assert everything is cleared
    assert metrics_mod._ACTIVE_REQUESTS == 0
    assert metrics_mod._MODEL_LOADED == 0
    assert len(_REQUEST_COUNTS) == 0
    assert len(_ERROR_COUNTS) == 0
    assert len(_REQUEST_DURATION_COUNT) == 0
    assert len(_REQUEST_DURATION_SUM) == 0
    assert len(_REQUEST_HISTOGRAM) == 0


def test_set_model_loaded():
    reset_metrics()
    set_model_loaded(True)
    assert "nlp_policy_nz_model_loaded 1" in render_metrics()
    set_model_loaded(False)
    assert "nlp_policy_nz_model_loaded 0" in render_metrics()


def test_active_requests():
    reset_metrics()
    increment_active_requests()
    assert "nlp_policy_nz_active_requests 1" in render_metrics()
    increment_active_requests()
    assert "nlp_policy_nz_active_requests 2" in render_metrics()
    decrement_active_requests()
    assert "nlp_policy_nz_active_requests 1" in render_metrics()
    decrement_active_requests()
    assert "nlp_policy_nz_active_requests 0" in render_metrics()
    # Ensure it doesn't go below zero
    decrement_active_requests()
    assert "nlp_policy_nz_active_requests 0" in render_metrics()


def test_record_request():
    reset_metrics()
    record_request(
        method="GET", endpoint="/health", status=200, scope="public", duration_seconds=0.015
    )

    assert _REQUEST_COUNTS[("GET", "/health", 200, "public")] == 1
    assert _REQUEST_DURATION_COUNT[("GET", "/health")] == 1
    assert math.isclose(_REQUEST_DURATION_SUM[("GET", "/health")], 0.015, rel_tol=1e-9)
    assert len(_ERROR_COUNTS) == 0

    # Check buckets
    buckets = _REQUEST_HISTOGRAM[("GET", "/health")]
    # Duration 0.015 should land in bucket for 0.025 (which is index 2: 0.005, 0.01, 0.025)
    assert buckets[2] == 1
    assert buckets[0] == 0
    assert buckets[1] == 0

    # Error request
    record_request(method="POST", endpoint="/data", status=404, scope="api", duration_seconds=12.0)
    assert _ERROR_COUNTS[(404, "/data", "api")] == 1

    # Histogram fall-through (+Inf)
    # Duration 12.0 is greater than the max bucket 10.0
    buckets_post = _REQUEST_HISTOGRAM[("POST", "/data")]
    assert buckets_post[-1] == 1  # the +Inf bucket


def test_render_labels():
    labels = {"method": "GET", "status": 200}
    assert _render_labels(labels) == 'method="GET",status="200"'


def test_render_metrics():
    reset_metrics()
    set_model_loaded(True)
    increment_active_requests()
    record_request(method="GET", endpoint="/test", status=200, scope="public", duration_seconds=0.1)
    record_request(method="GET", endpoint="/test", status=200, scope="public", duration_seconds=0.2)
    record_request(
        method="POST", endpoint="/error", status=500, scope="private", duration_seconds=1.5
    )

    output = render_metrics()

    # Check gauges
    assert "nlp_policy_nz_active_requests 1" in output
    assert "nlp_policy_nz_model_loaded 1" in output

    # Check request count
    assert (
        'nlp_policy_nz_requests_total{method="GET",endpoint="/test",status="200",scope="public"} 2'
        in output
    )
    assert (
        'nlp_policy_nz_requests_total{method="POST",endpoint="/error",status="500",scope="private"} 1'
        in output
    )

    # Check errors
    assert 'nlp_policy_nz_errors_total{status="500",endpoint="/error",scope="private"} 1' in output

    # Check histograms and count/sum
    assert 'nlp_policy_nz_request_duration_seconds_count{method="GET",endpoint="/test"} 2' in output
    # checking float summation is tricky due to float imprecision in formatting, checking approx
    assert (
        'nlp_policy_nz_request_duration_seconds_sum{method="GET",endpoint="/test"} 0.3' in output
        or "0.3000" in output
    )
    assert (
        'nlp_policy_nz_request_duration_seconds_count{method="POST",endpoint="/error"} 1' in output
    )
    assert (
        'nlp_policy_nz_request_duration_seconds_sum{method="POST",endpoint="/error"} 1.5' in output
    )

    # Check that +Inf bucket exists and has correct cumulative count
    assert (
        'nlp_policy_nz_request_duration_seconds_bucket{method="GET",endpoint="/test",le="+Inf"} 2'
        in output
    )
    assert (
        'nlp_policy_nz_request_duration_seconds_bucket{method="POST",endpoint="/error",le="+Inf"} 1'
        in output
    )


def test_thread_safety():
    reset_metrics()
    num_threads = 20
    requests_per_thread = 100

    def worker():
        for _ in range(requests_per_thread):
            increment_active_requests()
            record_request(
                method="GET",
                endpoint="/concurrency",
                status=200,
                scope="public",
                duration_seconds=0.1,
            )
            decrement_active_requests()

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker) for _ in range(num_threads)]
        concurrent.futures.wait(futures)

    # Verify exact counts despite concurrent access
    assert "nlp_policy_nz_active_requests 0" in render_metrics()
    assert (
        _REQUEST_COUNTS[("GET", "/concurrency", 200, "public")] == num_threads * requests_per_thread
    )
    assert _REQUEST_DURATION_COUNT[("GET", "/concurrency")] == num_threads * requests_per_thread

    # Use math.isclose for float comparison
    expected_sum = num_threads * requests_per_thread * 0.1
    actual_sum = _REQUEST_DURATION_SUM[("GET", "/concurrency")]
    assert math.isclose(actual_sum, expected_sum, rel_tol=1e-9)
