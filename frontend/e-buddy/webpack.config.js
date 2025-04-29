const path = require('path');

module.exports = {
  mode: 'production',
  entry: {
    'chat-widget': './src/chat-widget-entry.tsx',
    'chat-widget-loader': './public/chat-widget-loader.js'
  },
  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, 'public'),
    library: '[name]',
    libraryTarget: 'umd',
    globalObject: 'this',
  },
  resolve: {
    extensions: ['.ts', '.tsx', '.js'],
    alias: { '@': path.resolve(__dirname, 'src') },
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: [
          {
            loader: 'ts-loader',
            options: {
              transpileOnly: true,
              compilerOptions: { noEmit: false, jsx: 'react-jsx' },
            },
          },
        ],
        exclude: /node_modules/,
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader', 'postcss-loader'],
      },
    ],
  },
};