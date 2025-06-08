import chart as ch
import rpe
import json
chart = input('Chart file: ')
chartjson = json.load(open(chart, encoding='utf-8'))
if 'META' in chartjson:
    chart = rpe.RPE(chartjson)
else:
    chart = ch.Chart(chartjson, {}, '')
print('Note Count:', chart.notes)
print('Line Count:', len(chart.lines))
while True:
    x = input()
    try:
        print(eval(x))
    except Exception as e:
        print(e)