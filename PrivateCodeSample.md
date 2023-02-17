# 가상환경 확인
conda env list
# 가상환경 생성
set CONDA_FORCE_32BIT=1
conda create -n 이름 python=3.8
# 가상환경 활성화
conda activate 이름
# 가상환경 비활성화
conda deactivate
# 가상환경 삭제
conda remove -n 가상환경이름 --all