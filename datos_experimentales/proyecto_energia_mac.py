#!/usr/bin/env python3
"""Prueba piloto de energia de Selection Sort vs Merge Sort con powermetrics en macOS.

Ejecutar en Mac: sudo -v && python3 proyecto_energia_mac.py
Analizar sin hardware: python3 proyecto_energia_mac.py --analizar-directorio resultados_energia

Solo biblioteca estandar. Las estimaciones de potencia son del conjunto de CPUs, no del proceso.
"""
import argparse
import csv
import datetime as dt
import json
import math
import os
from pathlib import Path
import random
import re
import shutil
import signal
import statistics
import subprocess
import sys
import time

SECTION = re.compile(r'\*\*\* Sampled system activity \(([^\n()]*)\) \(([0-9.]+)ms elapsed\) \*\*\*')
POWER = re.compile(r'^CPU Power:\s*([0-9.]+) mW', re.M)


def selection_sort(sequence):
    v = list(sequence)
    for i in range(len(v)-1):
        smallest = i
        for j in range(i+1, len(v)):
            if v[j] < v[smallest]:
                smallest = j
        v[i], v[smallest] = v[smallest], v[i]
    return v


def merge_sort(sequence):
    # Recursion and merge written by the students; no built-in sort used here.
    if len(sequence) <= 1:
        return list(sequence)
    m = len(sequence) // 2
    left = merge_sort(sequence[:m]); right = merge_sort(sequence[m:])
    result = []; i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:]); result.extend(right[j:])
    return result


def parse_power(path):
    raw = Path(path).read_text(encoding='utf-8', errors='replace')
    matches = list(SECTION.finditer(raw))
    records = []
    for i, found in enumerate(matches):
        text = raw[found.end(): matches[i+1].start() if i+1 < len(matches) else len(raw)]
        p = POWER.search(text)
        if not p:
            continue
        try:
            end = dt.datetime.strptime(found.group(1).strip(), '%a %b %d %H:%M:%S %Y %z').timestamp()
            duration = float(found.group(2)) / 1000.0
        except ValueError:
            continue
        records.append({'end':end, 'dt': duration, 'p_w': float(p.group(1))/1000.0})
    return records


def samples_in_phase(records, phase):
    # Powermetrics labels only to the second; exclude boundary-overlapping samples.
    # A sample's timestamp marks the end of its averaging window.
    left = phase['start'] + 1.0
    right = phase['end'] - 1.0
    return [r for r in records if r['end'] - r['dt'] >= left and r['end'] <= right]


def weighted_mean(samples):
    return sum(s['p_w'] * s['dt'] for s in samples) / sum(s['dt'] for s in samples)


def safe_mean(values):
    return statistics.mean(values) if values else float('nan')


def analyze(directory):
    d = Path(directory)
    meta = json.loads((d/'eventos.json').read_text(encoding='utf-8'))
    records = parse_power(d/'potencia.txt')
    if not records:
        raise RuntimeError('No se encontraron muestras CPU Power: comprueba que powermetrics produjo datos.')
    phases = meta['phases']
    for p in phases:
        matches = samples_in_phase(records, p)
        p['samples'] = len(matches)
        p['power_w'] = weighted_mean(matches) if matches else float('nan')
        p['power_sd_w'] = statistics.stdev([a['p_w'] for a in matches]) if len(matches)>1 else float('nan')

    baselines = [p['power_w'] for p in phases if p['kind']=='baseline' and math.isfinite(p['power_w'])]
    if not baselines:
        raise RuntimeError('No hay muestras de reposo incluidas enteramente dentro de los intervalos.')
    base = statistics.mean(baselines)
    rows = []
    for p in phases:
        if p['kind']!='sort':
            continue
        watts = p['power_w']
        t = p['end']-p['start']
        count = p['executions']
        p_total = watts*t
        p_extra = (watts-base)*t
        rows.append({
            'algoritmo':p['name'], 'n':p['n'],
            'ejecuciones':count, 'duracion_s':round(t,4),
            'muestras_potencia':p['samples'],
            'potencia_media_cpu_W':round(watts,5),
            'potencia_reposo_W':round(base,5),
            'energia_cpu_total_J':round(p_total,5),
            'energia_cpu_adicional_estimada_J':round(p_extra,5),
            'energia_adicional_por_ordenamiento_J':round(p_extra/count,9),
            'tiempo_por_ordenamiento_s':round(t/count,8),
        })
    with (d/'resultados.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    print('\nRESUMEN DE ENERGIA ESTIMADA (CPU COMPLETA, NO PROCESO AISLADO)')
    print('Muestras totales powermetrics:',len(records))
    print('Potencia media de referencia: %.3f W'%base)
    print('Reposo medido al inicio/final:',[round(b,3) for b in baselines])
    print('%16s %6s %9s %10s %12s %12s'%('algoritmo','n','ejec.','P_cpu(W)','E_adic(J)','E/orden.(J)'))
    for r in rows:
        print('%16s %6d %9d %10.3f %12.2f %12.7f'%(
            r['algoritmo'],r['n'],r['ejecuciones'],r['potencia_media_cpu_W'],
            r['energia_cpu_adicional_estimada_J'],r['energia_adicional_por_ordenamiento_J']))

    # Independent held-out size: first two n to calibrate, final n to evaluate.
    validation = ['VALIDACION DEL MODELO E = c * operaciones_aproximadas']
    for name in ('Selection Sort', 'Merge Sort'):
        chosen = sorted([r for r in rows if r['algoritmo']==name], key=lambda r:r['n'])
        if len(chosen)<3 or any(r['energia_adicional_por_ordenamiento_J']<=0 for r in chosen):
            validation.append(name+': no se puede evaluar con fiabilidad (faltan tamaños o energia adicional positiva).')
            continue
        def proxy(n):
            return n*(n-1)/2 if name=='Selection Sort' else n*math.log2(n)
        training = chosen[:-1]; test = chosen[-1]
        c = sum(proxy(r['n'])*r['energia_adicional_por_ordenamiento_J'] for r in training)/sum(proxy(r['n'])**2 for r in training)
        prediction = c*proxy(test['n']); actual = test['energia_adicional_por_ordenamiento_J']
        error = abs(prediction-actual)/abs(actual)*100
        validation.append(f"{name}, n={test['n']}: medido={actual:.6g} J/ord., predicho={prediction:.6g} J/ord., error relativo={error:.1f}%")
    with (d/'validacion.txt').open('w', encoding='utf-8') as f:
        f.write('\n'.join(validation)+'\n')
    for line in validation: print(line)
    print('\nArchivos:',d/'resultados.csv', 'y',d/'validacion.txt')
    print('IMPORTANTE: el consumo extra depende del estado del sistema y NO es energia exacta del proceso.')
    print('Una sola prueba por tamano es EXPLORATORIA. Para conclusiones formales: varias repeticiones alternadas.')


def run(args):
    if sys.platform!='darwin':
        raise SystemExit('La medicion automatica requiere macOS. --analizar-directorio funciona en otros sistemas.')
    if not shutil.which('powermetrics'):
        raise SystemExit('No se encontro powermetrics.')
    if not shutil.which('sudo'):
        raise SystemExit('No se encontro sudo.')
    testrun = subprocess.run(['sudo','-n','true'],capture_output=True)
    if testrun.returncode:
        raise SystemExit('Primero ejecutar: sudo -v   (e ingresar contrasena en Terminal).')

    d = Path(args.salida).expanduser().resolve(); d.mkdir(parents=True,exist_ok=True)
    power_log = d/'potencia.txt'
    print('Iniciando powermetrics...')
    monitor = subprocess.Popen(['sudo','-n','powermetrics','--samplers','cpu_power',
                                '-i','1000','-o',str(power_log)],
                                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                start_new_session=True)
    phases=[]
    try:
        time.sleep(2.5)
        if monitor.poll() is not None:
            raise RuntimeError('powermetrics termino anticipadamente: '+monitor.stderr.read().decode(errors='replace'))
        def baseline(label):
            print('Fase:',label,flush=True)
            start=time.time(); time.sleep(args.reposo); end=time.time()
            phases.append({'kind':'baseline','name':label,'start':start,'end':end})
        baseline('reposo inicial')
        cases=[('Selection Sort', selection_sort),('Merge Sort',merge_sort)]
        # Alternate algorithm order with n to reduce systematic time/order bias.
        for k,n in enumerate(args.tamanos):
            order = cases if k%2==0 else list(reversed(cases))
            original=list(range(n)); random.Random(314159+n).shuffle(original)
            expected=sorted(original)
            for name, sort_fn in order:
                if sort_fn(original)!=expected:
                    raise AssertionError(f'El algoritmo {name} no ordena correctamente.')
                print(f'Fase: {name} n={n}',flush=True)
                start=time.time(); t0=time.perf_counter();count=0;checksum=0
                while time.perf_counter()-t0<args.segundos:
                    result=sort_fn(original)
                    checksum+=result[-1];count+=1
                end=time.time()
                phases.append({'kind':'sort','name':name,'n':n,'executions':count,
                               'start':start,'end':end,'checksum':checksum})
                time.sleep(2.0)
        baseline('reposo final')
    finally:
        # Stop only our own process group; do not kill other powermetrics instances.
        if monitor.poll() is None:
            try: os.killpg(monitor.pid,signal.SIGINT)
            except ProcessLookupError: pass
        try: monitor.wait(timeout=8)
        except subprocess.TimeoutExpired:
            try: os.killpg(monitor.pid,signal.SIGTERM)
            except ProcessLookupError: pass
            monitor.wait(timeout=5)
    (d/'eventos.json').write_text(json.dumps({'phases':phases,'sizes':args.tamanos},indent=2,ensure_ascii=False),encoding='utf-8')
    # Check / print only if output exists and contains sufficient data.
    analyze(d)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--salida',default='resultados_energia', help='Carpeta de archivos de medicion')
    p.add_argument('--tamanos',type=int,nargs='+',default=[500,1000,2000])
    p.add_argument('--segundos',type=float,default=12,help='Duracion de cada carga en segundos')
    p.add_argument('--reposo',type=float,default=10,help='Duracion de cada reposo en segundos')
    p.add_argument('--analizar-directorio',default=None,help='Solo procesar resultados existentes')
    args=p.parse_args()
    if args.analizar_directorio:
        analyze(args.analizar_directorio)
    else:
        if len(args.tamanos)<3: raise SystemExit('Se requieren tres tamanos para la validacion con un tamano reservado.')
        if args.segundos<6 or args.reposo<6: raise SystemExit('Usa intervalos >=6s para obtener suficientes muestras de potencia.')
        run(args)

if __name__=='__main__': main()
