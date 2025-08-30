FROM condaforge/mambaforge

WORKDIR /app

# 复制环境配置文件
COPY environment.yml .

# 使用mamba创建环境
RUN mamba env create -f environment.yml

# 初始化conda并激活环境
RUN echo "source activate edu_feedback_analysis" > ~/.bashrc
ENV PATH /opt/conda/envs/edu_feedback_analysis/bin:$PATH

# 安装额外的pip依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
