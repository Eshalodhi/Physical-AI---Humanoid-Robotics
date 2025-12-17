// @ts-check
import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'A Hands-On Guide to Embodied Intelligence',
  favicon: 'img/favicon.ico',

  // Production URL
  url: 'https://your-username.github.io',
  baseUrl: '/Physical-AI---Humanoid-Robotics/',

  // GitHub pages deployment config
  organizationName: 'your-username',
  projectName: 'physical-ai-robotics-book',

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',
  onBrokenAnchors: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl: 'https://github.com/your-username/physical-ai-robotics-book/tree/main/book/',
          showLastUpdateTime: false,
          showLastUpdateAuthor: false,
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/social-card.jpg',
      navbar: {
        title: 'Physical AI Book',
        logo: {
          alt: 'Physical AI Book Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'bookSidebar',
            position: 'left',
            label: 'Book',
          },
          {
            type: 'dropdown',
            label: 'Modules',
            position: 'left',
            items: [
              {
                label: 'Introduction',
                to: '/docs/category/introduction',
              },
              {
                label: 'Module 1: ROS 2',
                to: '/docs/category/module-1-ros-2-fundamentals',
              },
              {
                label: 'Module 2: Simulation',
                to: '/docs/category/module-2-simulation',
              },
              {
                label: 'Module 3: NVIDIA Isaac',
                to: '/docs/category/module-3-nvidia-isaac',
              },
              {
                label: 'Module 4: VLA',
                to: '/docs/category/module-4-vision-language-action',
              },
            ],
          },
          {
            href: 'https://github.com/your-username/physical-ai-robotics-book',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Book',
            items: [
              {
                label: 'Introduction',
                to: '/docs/category/introduction',
              },
              {
                label: 'ROS 2 Fundamentals',
                to: '/docs/category/module-1-ros-2-fundamentals',
              },
              {
                label: 'Simulation',
                to: '/docs/category/module-2-simulation',
              },
            ],
          },
          {
            title: 'Advanced',
            items: [
              {
                label: 'NVIDIA Isaac',
                to: '/docs/category/module-3-nvidia-isaac',
              },
              {
                label: 'VLA Models',
                to: '/docs/category/module-4-vision-language-action',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/your-username/physical-ai-robotics-book',
              },
              {
                label: 'ROS 2 Docs',
                href: 'https://docs.ros.org/en/humble/',
              },
              {
                label: 'NVIDIA Isaac',
                href: 'https://docs.nvidia.com/isaac/',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics Book. Built with Docusaurus. Last updated: December 2025.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['python', 'bash', 'yaml', 'json', 'markup'],
      },
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
      docs: {
        sidebar: {
          hideable: true,
          autoCollapseCategories: true,
        },
      },
    }),

  markdown: {
    mermaid: true,
  },
  themes: ['@docusaurus/theme-mermaid'],
};

export default config;
