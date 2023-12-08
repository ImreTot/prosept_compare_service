import { create } from 'zustand';

interface Test {}

const test = create<Test>((set) => ({
  activeId: undefined,
  setId: (id: string) => set({ activeId: id }),
}));

export default test;