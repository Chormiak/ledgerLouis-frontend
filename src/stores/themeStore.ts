import { defineStore } from 'pinia';
import { ref } from 'vue';

type Theme = 'light' | 'dark';

const STORAGE_KEY = 'theme';

const getInitialTheme = (): Theme => {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved === 'dark' || saved === 'light') return saved;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<Theme>(getInitialTheme());

  const applyTheme = (value: Theme) => {
    document.documentElement.setAttribute('data-theme', value);
    localStorage.setItem(STORAGE_KEY, value);
  };

  const setTheme = (value: Theme) => {
    theme.value = value;
    applyTheme(value);
  };

  const toggleTheme = () => {
    setTheme(theme.value === 'dark' ? 'light' : 'dark');
  };

  const initTheme = () => {
    applyTheme(theme.value);
  };

  return {
    theme,
    setTheme,
    toggleTheme,
    initTheme,
  };
});
