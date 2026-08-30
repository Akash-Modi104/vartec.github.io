const { copyFileSync, existsSync, unlinkSync, writeFileSync } = require('fs');
const { join } = require('path');

const outputDirectory = join(process.cwd(), 'docs');
const indexFile = join(outputDirectory, 'index.html');

if (!existsSync(indexFile)) {
  throw new Error('GitHub Pages build is missing docs/index.html');
}

copyFileSync(indexFile, join(outputDirectory, '404.html'));

const originalIndexFile = join(outputDirectory, 'index.original.html');
if (existsSync(originalIndexFile)) {
  unlinkSync(originalIndexFile);
}

const noJekyllFile = join(outputDirectory, '.nojekyll');
if (!existsSync(noJekyllFile)) {
  writeFileSync(noJekyllFile, '');
}

console.log('GitHub Pages fallback and .nojekyll files are ready.');
