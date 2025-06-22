@echo off
cd /d "C:\Users\amaan\.lmstudio\models\lmstudio-community\Mistral-7B-Instruct-v0.3-GGUF"
echo Running LLaMA server...
llama-server -m Mistral-7B-Instruct-v0.3-Q4_K_M.gguf --n-gpu-layers 20 --port 8080 --ctx-size 2048 --threads 6