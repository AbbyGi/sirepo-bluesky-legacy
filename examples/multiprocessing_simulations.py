from multiprocessing import Process
from sirepo_bluesky import SirepoBluesky
import hashlib
import time

# use the "Youngs Double Slit Experiment" example simulation
sim_id = '87XJ4oEb'
sb = SirepoBluesky('http://10.10.10.10:8000')
sb.auth('srw', sim_id)


def run(sim):
    print('running sim {}'.format(sim.sim_id))
    sim.run_simulation()


def main():
    copies = []
    COPY_COUNT = 10
    RUN_PARALLEL = True

    start_time = time.time()
    for i in range(COPY_COUNT):
        # name doesn't need to be unique, server will rename it
        c1 = sb.copy_sim('{} Bluesky'.format(sb.data['models']['simulation']['name']),)
        print('copy {}, {}'.format(c1.sim_id, c1.data['models']['simulation']['name']))
        # vary an aperture position
        aperture = c1.find_element(c1.data['models']['beamline'], 'title', 'Aperture')
        aperture['position'] = float(aperture['position']) + 0.5 * (i + 1)
        watch = sb.find_element(c1.data['models']['beamline'], 'title', 'W60')
        c1.data['report'] = 'watchpointReport{}'.format(watch['id'])
        copies.append(c1)
    cc_time = time.time()

    if RUN_PARALLEL:
        procs = []
        for i in range(COPY_COUNT):
            p = Process(target=run, args=(copies[i],))
            p.start()
            procs.append(p)
        # wait for procs to finish
        for p in procs:
            p.join()
    else:
        # run serial
        for i in range(COPY_COUNT):
            print('running sim: {}', copies[i].sim_id)
            copies[i].run_simulation()
    mp_time = time.time()
    # get results and clean up the copied simulations
    for i in range(COPY_COUNT):
        f = copies[i].get_datafile()
        print(f)
        print('copy {} data hash: {}'.format(copies[i].sim_id, hashlib.md5(f).hexdigest()))
        copies[i].delete_copy()
    clean_time = time.time()
    print('Copy creation time:', cc_time - start_time)
    print('Multiprocessing time:', mp_time - cc_time)
    print('Clean up time:', clean_time - mp_time)
    print('Total time:', clean_time - start_time)


if __name__ == '__main__':
    main()
