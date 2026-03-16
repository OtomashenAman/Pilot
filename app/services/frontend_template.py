import os


STARTER_FILES = {
    "frontend/web/package.json": """{
  "name": "compliance-web",
  "private": true,
  "scripts": {
    "dev": "next dev -p 3000",
    "build": "next build",
    "start": "next start -p 3000",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.2.15",
    "react": "18.3.1",
    "react-dom": "18.3.1"
  },
  "devDependencies": {
    "@types/node": "22.7.4",
    "@types/react": "18.3.3",
    "@types/react-dom": "18.3.0",
    "autoprefixer": "10.4.20",
    "postcss": "8.4.47",
    "tailwindcss": "3.4.13",
    "typescript": "5.6.2"
  }
}""",
    "frontend/web/next.config.js": """const nextConfig = { reactStrictMode: true };
module.exports = nextConfig;
""",
    "frontend/web/app/page.tsx": """export default function HomePage() {
  return <main className="p-6"><h1>Compliance AI Builder</h1></main>;
}
""",
}


def write_starter_frontend(base_dir: str):
    for rel_path, content in STARTER_FILES.items():
        path = os.path.join(base_dir, rel_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)