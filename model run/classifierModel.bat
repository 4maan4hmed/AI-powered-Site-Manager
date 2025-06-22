@echo off
cd /d "C:\Users\amaan\.lmstudio\models\4maan4hmad\Mistral-finetuned-sitemanager-v2.0"
echo Running LLaMA server...
llama-server -m unsloth.Q4_K_M.gguf --n-gpu-layers 20 --port 8080 --ctx-size 2048 --threads 6