import { DefaultTheme } from "vitepress/theme";

const sidebar: DefaultTheme.SidebarItem[] = [
  {text: 'Overview', link: '/folds/'},
  {
    text: 'Tutorial',
    items: [
      {text: 'Quick Start', link: '/folds/tutorial/quick-start'},
      {text: 'Simple Rules', link: '/folds/tutorial/rules'},
      {text: 'Rule Kinds', link: '/folds/tutorial/rule-kinds'},
      {text: 'Arguments', link: '/folds/tutorial/arguments'},
      {text: 'Multiple Files', link: '/folds/tutorial/multiple-files'},
    ]
  },
  {
    text: 'Advanced Features',
    items: [
      {text: 'Admin Rules', link: '/folds/advanced/admin'},
      {text: 'Multiple Bots', link: '/folds/advanced/multiple-bots'},
    ],
  },
  {
    text: 'Learn',
    items: [
      {text: 'Examples', link: '/folds/examples'},
    ],
  },
]

export default sidebar
