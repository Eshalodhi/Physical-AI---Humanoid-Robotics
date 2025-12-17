import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">{siteConfig.title}</h1>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/">
            Start Learning
          </Link>
        </div>
      </div>
    </header>
  );
}

function FeatureCard({title, description, link, linkText}) {
  return (
    <div className={clsx('col col--4')}>
      <div className={styles.featureCard}>
        <h3>{title}</h3>
        <p>{description}</p>
        <Link className="button button--primary button--sm" to={link}>
          {linkText}
        </Link>
      </div>
    </div>
  );
}

function WhyPhysicalAI() {
  return (
    <section className={styles.whySection}>
      <div className="container">
        <h2>Why Physical AI Matters</h2>
        <p className={styles.whyText}>
          The convergence of advanced AI models with physical robotics represents
          one of the most transformative technological shifts of our time. As large
          language models gain the ability to perceive, reason, and act in the
          physical world, humanoid robots are transitioning from science fiction
          to practical reality.
        </p>
        <p className={styles.whyText}>
          This book equips you with the complete skillset to build intelligent
          humanoid robots: from ROS 2 fundamentals to simulation, perception
          with NVIDIA Isaac, and cutting-edge Vision-Language-Action models.
          By the end, you'll have built a voice-controlled humanoid that can
          navigate, manipulate objects, and respond to natural language commands.
        </p>
      </div>
    </section>
  );
}

function ModulesOverview() {
  const modules = [
    {
      title: 'ROS 2 Fundamentals',
      description: 'Master the Robot Operating System 2 - the foundation for modern robotics development.',
      link: '/docs/category/module-1-ros-2-fundamentals',
      linkText: 'Module 1',
    },
    {
      title: 'Robot Simulation',
      description: 'Build and test humanoids in Gazebo and Unity before deploying to real hardware.',
      link: '/docs/category/module-2-simulation',
      linkText: 'Module 2',
    },
    {
      title: 'NVIDIA Isaac',
      description: 'Leverage GPU-accelerated perception, navigation, and synthetic data generation.',
      link: '/docs/category/module-3-nvidia-isaac',
      linkText: 'Module 3',
    },
    {
      title: 'Vision-Language-Action',
      description: 'Integrate LLMs and multimodal AI to create robots that understand natural language.',
      link: '/docs/category/module-4-vision-language-action',
      linkText: 'Module 4',
    },
    {
      title: 'Introduction',
      description: 'Understand Physical AI foundations, the digital-to-physical gap, and sensor systems.',
      link: '/docs/category/introduction',
      linkText: 'Start Here',
    },
    {
      title: 'GitHub Repository',
      description: 'Access all code examples, supplementary materials, and contribute to the project.',
      link: 'https://github.com/your-username/physical-ai-robotics-book',
      linkText: 'GitHub',
    },
  ];

  return (
    <section className={styles.modulesSection}>
      <div className="container">
        <h2>Book Modules</h2>
        <div className="row">
          {modules.map((props, idx) => (
            <FeatureCard key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={siteConfig.title}
      description="A Hands-On Guide to Embodied Intelligence - Learn to build humanoid robots with ROS 2, simulation, NVIDIA Isaac, and VLA models">
      <HomepageHeader />
      <main>
        <WhyPhysicalAI />
        <ModulesOverview />
      </main>
    </Layout>
  );
}
