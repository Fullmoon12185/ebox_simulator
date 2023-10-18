1. Need Python > 3.6 (better get the latest one)
2. Go the the main folder and Create virtual environment:
python -m venv pythonEnv
3. source pythonEnv/bin/activate
4. cd simulator
5. pip3 install -r requirements.txt
6. Change box id in main.py file: On line range (9,9+numberOfBox), change to range (1110,1110+numberOfBox) with 1111 is box id
7. python3 ./main1.py