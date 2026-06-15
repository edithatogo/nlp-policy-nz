import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://edithatogo.github.io',
  base: '/nlp-policy-nz/',
  integrations: [
    mdx(),
    sitemap(),
    starlight({
      title: 'NLP Policy NZ',
      description: 'Legal NZ documentation portal for NLP Policy NZ.',
      sidebar: [
        { label: 'Start', items: ['index', 'docs-tooling-audit'] },
      ],
    }),
  ],
});
