/**
 * Swizzled Layout Component
 *
 * This wraps the default Docusaurus Layout to inject the RAG Chatbot
 * globally on every page.
 *
 * Created by running: npx docusaurus swizzle @docusaurus/theme-classic Layout --wrap
 * (But we're doing it manually for control)
 */

import React from 'react';
import Layout from '@theme-original/Layout';
import RagChatbot from '@site/src/components/RagChatbot';

export default function LayoutWrapper(props) {
  return (
    <>
      <Layout {...props} />
      <RagChatbot />
    </>
  );
}
