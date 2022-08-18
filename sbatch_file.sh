#!/bin/sh
#SBATCH --mail-user=juan.restrepo@uner.edu.ar
#SBATCH --partition=debug
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --error=./job.%J.err
#SBATCH --output=./job.%J.out
#SBATCH --job-name=ParseSleepDB
cd /home/jrestrepo/ParseSleepDB/
chmod 777 ./parseDataBase.py
export PYTHONUNBUFFERED=1
./parseDataBase.py >out01.txt 2>err01.txt
