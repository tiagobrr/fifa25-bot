#!/usr/bin/env bash
set -eux

# Baixa o Chrome diretamente e extrai
wget https://storage.googleapis.com/chrome-for-testing-public/124.0.6367.91/linux64/chrome-linux64.zip
unzip chrome-linux64.zip
mv chrome-linux64 /opt/chrome

# Exporta as variáveis de ambiente para o Chrome headless funcionar
echo "export CHROME_BIN=/opt/chrome/chrome" >> ~/.bashrc
echo "export PATH=$PATH:/opt/chrome" >> ~/.bashrc
