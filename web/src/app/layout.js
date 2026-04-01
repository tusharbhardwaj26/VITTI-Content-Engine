import './globals.css';

export const metadata = {
  title: 'Content Generator | Vitti Capital',
  description: 'AI-powered finance idea generation dashboard.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <main className="container">
          {children}
        </main>
      </body>
    </html>
  );
}
