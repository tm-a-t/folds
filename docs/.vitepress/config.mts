import { defineConfig } from 'vitepress'
import sidebar from "../folds/.site/sidebar";

export default defineConfig({
  title: "Folds Docs Preview",
  themeConfig: {
    sidebar,
  },
  cleanUrls: true,
})
