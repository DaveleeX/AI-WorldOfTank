import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = {title: 'IRON FRONT · 废土战线',description:'驾驶六国坦克，在废土战场展开 5v5 对战。'};
export default function RootLayout({children}: Readonly<{children: React.ReactNode}>) {return <html lang="zh-CN"><body>{children}</body></html>}
