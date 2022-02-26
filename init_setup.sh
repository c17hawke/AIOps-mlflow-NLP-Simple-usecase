conda create --prefix ./env python=3.7 -y
source C:/Users/sunny/miniconda3/etc/profile.d/conda.sh # use your username instead of sunny
source activate ./env
pip install -r requirements.txt
conda env export > conda.yaml