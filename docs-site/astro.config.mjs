import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import { astroExpressiveCode } from 'astro-expressive-code';
import sitemap from '@astrojs/sitemap';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://edithatogo.github.io',
  base: '/nlp-policy-nz/',
  integrations: [
    astroExpressiveCode(),
    mdx(),
    sitemap(),
    starlight({
      title: 'NLP Policy NZ',
      description: 'Legal NZ documentation portal for NLP Policy NZ.',
      sidebar: [
        { label: 'Start', items: ['index', 'quickstart', 'installation', 'versioning'] },
        {
          label: 'User guides',
          items: [
            'guides/ingestion',
            'guides/ontology',
            'guides/search',
            'guides/publishing',
            'guides/client-sdk',
          ],
        },
        {
          label: 'Reference',
          items: ['api/openapi', 'api/python', 'api/cli'],
        },
        {
          label: 'Architecture',
          items: [
            'architecture/system-overview',
            'architecture/data-flow',
            'architecture/ontology-kg',
            'architecture/security',
            'architecture/adr',
          ],
        },
        {
          label: 'Operations',
          items: ['operations/runbook'],
        },
        {
          label: 'Tutorials',
          items: [
            'tutorials/hansard-stance-citations',
            'tutorials/semantic-legislation-search',
            'tutorials/policy-argument-trace',
          ],
        },
        { label: 'Audit', items: ['docs-tooling-audit'] },
      ],
    }),
  ],
});
