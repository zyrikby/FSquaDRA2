'''
Created on Feb 24, 2016

@author: Yury Zhauniarovich
'''
import os, csv, time, zipfile, argparse 
import threading, multiprocessing, Queue
import metrics

META_MANIFEST_REL_PATH = "META-INF/MANIFEST.MF"
FILE_PATH_KEY = "Name"
FILE_HASH_KEY = "SHA1-Digest"


IN_QUEUE_SIZE = 100
OUT_QUEUE_SIZE = 100
DEFAULT_PROCESSES_NUM = multiprocessing.cpu_count()
DEFAULT_TIMEOUT = 900



###############################################################################
class SimilarityScorerFactory():
    SCORE_TYPES = ["Block", "Cosine", "Dice", "Euclidian", "GeneralizedJaccard", 
                "GeneralizedOverlap", "Jaccard", "Overlap", "SimonWhite", "Tanimoto"]
    @staticmethod
    def get_scorers(scorer_types=SCORE_TYPES):
        score_classes = []
        for sc in scorer_types:
            score_classes.append(SimilarityScorerFactory._get_scorer(sc))
        return score_classes
    
    @staticmethod
    def _get_scorer(scorer_type):
        if scorer_type == "Block":
            return metrics.Block()
        if scorer_type == "Cosine":
            return metrics.Cosine()
        if scorer_type == "Dice":
            return metrics.Dice()
        if scorer_type == "Euclidian":
            return metrics.Euclidian()
        if scorer_type == "GeneralizedJaccard":
            return metrics.GeneralizedJaccard()
        if scorer_type == "GeneralizedOverlap":
            return metrics.GeneralizedOverlap()
        if scorer_type == "Jaccard":
            return metrics.Jaccard()
        if scorer_type == "Overlap":
            return metrics.Overlap()
        if scorer_type == "SimonWhite":
            return metrics.SimonWhite()
        if scorer_type == "Tanimoto":
            return metrics.Tanimoto()
        print "%s is not supported!" % scorer_type
        raise Exception("%s is not supported!" % scorer_type)


################################################################################
class QueuePopulatorThread(threading.Thread):
    def __init__(self, queue_to_populate, directory, pairs_file=None):
        threading.Thread.__init__(self)
        self._queue = queue_to_populate
        self._directory = directory
        self._pairs_file = pairs_file
        
    def run(self):
        print "Starting populating input queue..."
        if self._pairs_file:
            with open(self._pairs_file, 'rt') as infile:
                reader = csv.reader(infile, delimiter=',', quoting=csv.QUOTE_NONE)
                for indx, row in enumerate(reader):
                    if indx == 0:
                        continue
                    app1 = row[0]
                    app2 = row[1]
                    if not app1.endswith(".apk"):
                        app1 += ".apk"
                    if not app2.endswith(".apk"):
                        app2 += ".apk"
                    app_pair = (app1, app2)
                    self._queue.put(app_pair)
        else:
            apk_files = []
            for f in os.listdir(self._directory):
                if f.endswith('.apk'):
                    apk_files.append(f)
            num_of_files = len(apk_files)
            for app1_index in xrange(num_of_files):
                for app2_index in xrange(app1_index+1, num_of_files):
                    app1 = apk_files[app1_index]
                    app2 = apk_files[app2_index]
                    app_pair = (app1, app2)
                    self._queue.put(app_pair)

        print "Population of the input queue is done..."

################################################################################

class FileWriterThread(threading.Thread):
    def __init__(self, queue_with_results, out_file_path, fieldnames):
        threading.Thread.__init__(self)
        self._queue = queue_with_results
        self._out_file_path = out_file_path
        self._fieldnames=fieldnames
        self._exit = threading.Event()
        self._counter = 0
    
    def run(self):
        print "Starting thread to write results into the file %s..." % self._out_file_path
        with open(self._out_file_path, 'wt', buffering=1) as csvfile:
            #writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONE)
            dict_writer = csv.DictWriter(csvfile, self._fieldnames)
            dict_writer.writeheader()
            while not self._exit.is_set():
                while True:
                    queue_item=None
                    try:
                        queue_item = self._queue.get(True, 5)
                    except Queue.Empty:
                        break
                    dict_writer.writerow(queue_item)
                    self._counter += 1
                    self._queue.task_done()
                    if self._counter % 10 == 0:
                        print "Analyzed %d pairs..." % self._counter
            
        print "Finishing file writer thread..."
    
    def stop_thread(self):
        self._exit.set()
        
################################################################################

class ScorererProcessorPool():
    def __init__(self, in_queue, out_queue, samples_directory, scorerers, threads, timeout):
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.samples_directory = samples_directory
        self.scorerers = scorerers
        self.threads = threads
        self.timeout = timeout
        
        self._pool = []
        self._exit = multiprocessing.Event()
        
    def process(self):
        while not self._exit.is_set():
            while True:
                data = None
                try:
                    data = self.in_queue.get(True, 5)
                except Queue.Empty:
                    break
                apk1, apk2 = data
                
                result = self.get_scores_in_processes(apk1, apk2)
                
                self.out_queue.put(result)
                self.in_queue.task_done()
            
    
    def start_processes(self):
        for i in xrange(self.threads):
            proc = multiprocessing.Process(target=self.process)
            print "Starting process: ", proc.name
            proc.start()
            self._pool.append(proc)
    
    def stop_processes(self):
        self._exit.set()
        for proc in self._pool:
            print "Stopping process: ", proc.name
            proc.join()
    
    
    def get_scores_in_processes(self, apk1, apk2):
        print "Processing pair: [%s]  [%s]" % (apk1, apk2)
        res_queue = multiprocessing.Queue(5)
        p = multiprocessing.Process(target=get_app_pair_score, args=(res_queue, apk1, apk2,  
            self.samples_directory, self.scorerers))
        p.start()
        
        # Wait for TIMEOUT seconds or until process finishes
        p.join(self.timeout)
        result = None
        # If process is still active
        if p.is_alive():
            print "running... let's kill it..."
            # Terminate
            p.terminate()
            time.sleep(3)
            result = {
                "apk1" : apk1,
                "apk2" : apk2, 
                "result" : "terminated"
            }
        else:
            result = res_queue.get()
            time.sleep(1)
        
        p.join()
        res_queue = None
        p = None
        return result

################################################################################

def get_app_pair_score(res_queue, apk1, apk2, directory, scorerers):
    apk1_path = os.path.join(directory, apk1)
    apk2_path = os.path.join(directory, apk2)
    
    app_pair_comp_result = {
        "apk1" : apk1,
        "apk2" : apk2,
    }
    
    
    apk1_entries = get_file_hash_entries(apk1_path)
    if not apk1_entries:
        app_pair_comp_result.update({"result" : "apk1_missing_mf_entries"})
        return
    
    apk2_entries = get_file_hash_entries(apk2_path)
    if not apk2_entries:
        app_pair_comp_result.update({"result" : "apk2_missing_mf_entries"})
        return
    
    for scorerer in scorerers:
        scorerer_name = scorerer.get_name()
        for k in RES_TYPE_NAMES.keys():
            app1_hashes_k = get_resource_hashes(apk1_entries, k)
            if not app1_hashes_k:
                app_pair_comp_result.update({"%s_%s" % (scorerer_name, RES_TYPE_NAMES[k]) : "N/A" })
                continue
            app2_hashes_k = get_resource_hashes(apk2_entries, k)
            if not app2_hashes_k:
                app_pair_comp_result.update({"%s_%s" % (scorerer_name, RES_TYPE_NAMES[k]) : "N/A" })
                continue
            score_k = scorerer.compare(app1_hashes_k, app2_hashes_k)
            app_pair_comp_result.update({"%s_%s" % (scorerer_name, RES_TYPE_NAMES[k]) : "%.8f" % score_k })
            
    app_pair_comp_result.update({"result" : "ok"})
    res_queue.put(app_pair_comp_result)



RES_TYPE_ALL                     =  0
RES_TYPE_MANIFEST                =  1
RES_TYPE_ARSC                    =  2
RES_TYPE_MAIN_CODE               =  3
RES_TYPE_LIBS                    =  4
RES_TYPE_ASSETS                  =  5
RES_TYPE_RES_ALL                 =  6
RES_TYPE_RES_RAW                 =  7
RES_TYPE_RES_XML                 =  8
RES_TYPE_RES_DRAWABLE            =  9
RES_TYPE_RES_MENU                = 10
RES_TYPE_RES_LAYOUT              = 11
RES_TYPE_RES_ANIM                = 12
RES_TYPE_RES_COLOR               = 13
RES_TYPE_NATIVE_LIBS             = 14
RES_TYPE_CODE_GENERAL            = 15
RES_TYPE_AUDIO_VIDEO             = 16
RES_TYPE_IMAGES                  = 17
RES_TYPE_ALL_XML                 = 18


RES_TYPE_NAMES = {
    RES_TYPE_ALL : "all_files",
    RES_TYPE_MANIFEST : "manifest",
    RES_TYPE_MAIN_CODE : "main_code",
    RES_TYPE_ARSC : "resources_arsc",
    RES_TYPE_LIBS : "libs",
    RES_TYPE_ASSETS : "assets",
    RES_TYPE_RES_ALL : "res_all",
    RES_TYPE_RES_RAW : "res_raw",
    RES_TYPE_RES_XML : "res_xml",
    RES_TYPE_RES_DRAWABLE : "res_drawable",
    RES_TYPE_RES_MENU : "res_menu",
    RES_TYPE_RES_LAYOUT : "res_layout",
    RES_TYPE_RES_MENU : "res_menu",
    RES_TYPE_RES_ANIM : "res_anim",
    RES_TYPE_RES_COLOR : "res_color",
    RES_TYPE_NATIVE_LIBS : "native_libs",
    RES_TYPE_CODE_GENERAL : "code_general",
    RES_TYPE_AUDIO_VIDEO : "audio_video",
    RES_TYPE_IMAGES : "images",
    RES_TYPE_ALL_XML : "all_xml",
    
} 

def get_resource_hashes(apk_mf_entries, res_type):
    hashes_list = list()
    if res_type == RES_TYPE_ALL:
        for mf_entry in apk_mf_entries:
            hashes_list.append(mf_entry[FILE_HASH_KEY])
    elif res_type == RES_TYPE_MANIFEST:
        for mf_entry in apk_mf_entries:
            if mf_entry[FILE_PATH_KEY] == "AndroidManifest.xml":
                hashes_list.append(mf_entry[FILE_HASH_KEY])
                break
    elif res_type == RES_TYPE_ARSC:
        for mf_entry in apk_mf_entries:
            pth = mf_entry[FILE_PATH_KEY].lower()
            if (pth == "resources.arsc"):
                hashes_list.append(mf_entry[FILE_HASH_KEY])
                break
    elif res_type == RES_TYPE_MAIN_CODE:
        for mf_entry in apk_mf_entries:
            pth = mf_entry[FILE_PATH_KEY].lower()
            if (pth.startswith("classes") and pth.endswith(".dex")):
                hashes_list.append(mf_entry[FILE_HASH_KEY])
    elif res_type == RES_TYPE_LIBS:
        for mf_entry in apk_mf_entries:
            pth = mf_entry[FILE_PATH_KEY].lower()
            if (pth.startswith("libs/") or pth.startswith("lib/")):
                hashes_list.append(mf_entry[FILE_HASH_KEY])
    elif res_type == RES_TYPE_ASSETS:
        for mf_entry in apk_mf_entries:
            pth = mf_entry[FILE_PATH_KEY].lower()
            if pth.startswith("assets/"):
                hashes_list.append(mf_entry[FILE_HASH_KEY])
    elif res_type == RES_TYPE_RES_ALL:
        for mf_entry in apk_mf_entries:
            pth = mf_entry[FILE_PATH_KEY].lower()
            if pth.startswith("res/"):
                hashes_list.append(mf_entry[FILE_HASH_KEY])
    elif res_type == RES_TYPE_RES_RAW:
        for mf_entry in apk_mf_entries:
            pth = mf_entry[FILE_PATH_KEY].lower()
            if pth.startswith("res/raw/"):
                hashes_list.append(mf_entry[FILE_HASH_KEY])
    elif res_type == RES_TYPE_RES_XML:
        for mf_entry in apk_mf_entries:
            pth = mf_entry[FILE_PATH_KEY].lower()
            if pth.startswith("res/xml/"):
                hashes_list.append(mf_entry[FILE_HASH_KEY])
    elif res_type == RES_TYPE_RES_DRAWABLE:
        for mf_entry in apk_mf_entries:
            pth = mf_entry[FILE_PATH_KEY].lower()
            if pth.startswith("res/drawable/"):
                hashes_list.append(mf_entry[FILE_HASH_KEY])
    elif res_type == RES_TYPE_RES_MENU:
        for mf_entry in apk_mf_entries:
            pth = mf_entry[FILE_PATH_KEY].lower()
            if pth.startswith("res/menu/"):
                hashes_list.append(mf_entry[FILE_HASH_KEY])
    elif res_type == RES_TYPE_RES_LAYOUT:
        for mf_entry in apk_mf_entries:
            pth = mf_entry[FILE_PATH_KEY].lower()
            if pth.startswith("res/layout/"):
                hashes_list.append(mf_entry[FILE_HASH_KEY])
    elif res_type == RES_TYPE_RES_ANIM:
        for mf_entry in apk_mf_entries:
            pth = mf_entry[FILE_PATH_KEY].lower()
            if pth.startswith("res/anim/"):
                hashes_list.append(mf_entry[FILE_HASH_KEY])
    elif res_type == RES_TYPE_RES_COLOR:
        for mf_entry in apk_mf_entries:
            pth = mf_entry[FILE_PATH_KEY].lower()
            if pth.startswith("res/color/"):
                hashes_list.append(mf_entry[FILE_HASH_KEY])
    elif res_type == RES_TYPE_RES_COLOR:
        for mf_entry in apk_mf_entries:
            pth = mf_entry[FILE_PATH_KEY].lower()
            if pth.startswith("res/color/"):
                hashes_list.append(mf_entry[FILE_HASH_KEY])

    elif res_type == RES_TYPE_NATIVE_LIBS:
        for mf_entry in apk_mf_entries:
            pth = mf_entry[FILE_PATH_KEY].lower()
            if pth.endswith(".so"):
                hashes_list.append(mf_entry[FILE_HASH_KEY])
    elif res_type == RES_TYPE_CODE_GENERAL:
        for mf_entry in apk_mf_entries:
            pth = mf_entry[FILE_PATH_KEY].lower()
            if (pth.endswith(".so") or 
                pth.endswith(".bin") or
                pth.endswith(".jar") or 
                pth.endswith(".dex")):
                hashes_list.append(mf_entry[FILE_HASH_KEY])
    elif res_type == RES_TYPE_AUDIO_VIDEO:
        for mf_entry in apk_mf_entries:
            pth = mf_entry[FILE_PATH_KEY].lower()
            if (pth.endswith(".ogg") or 
                pth.endswith(".acc") or 
                pth.endswith(".3gp") or 
                pth.endswith(".mp4") or 
                pth.endswith(".m4a") or 
                pth.endswith(".flac") or 
                pth.endswith(".mid") or 
                pth.endswith(".xmf") or 
                pth.endswith(".mxmf") or 
                pth.endswith(".rtttl") or 
                pth.endswith(".rtx") or 
                pth.endswith(".ota") or 
                pth.endswith(".imy") or 
                pth.endswith(".mkv") or 
                pth.endswith(".wav") or 
                pth.endswith(".mkv") or 
                pth.endswith(".ts") or 
                pth.endswith(".mp3")):
                hashes_list.append(mf_entry[FILE_HASH_KEY])
    elif res_type == RES_TYPE_IMAGES:
        for mf_entry in apk_mf_entries:
            pth = mf_entry[FILE_PATH_KEY].lower()
            if (pth.endswith(".png") or 
                pth.endswith(".jpg") or 
                pth.endswith(".jpeg") or 
                pth.endswith(".gif") or 
                pth.endswith(".webp") or 
                pth.endswith(".bmp")):
                hashes_list.append(mf_entry[FILE_HASH_KEY])
    elif res_type == RES_TYPE_ALL_XML:
        for mf_entry in apk_mf_entries:
            pth = mf_entry[FILE_PATH_KEY].lower()
            if pth.endswith(".xml"):
                hashes_list.append(mf_entry[FILE_HASH_KEY])

    return hashes_list
    


def get_file_hash_entries(apk_path):
    with zipfile.ZipFile(apk_path, 'r') as zf:
        #print apk_path, zf.namelist()
        manifest_data = None
        try:
            manifest_data = zf.read(META_MANIFEST_REL_PATH)
        except KeyError:
            manifest_path = None
            zf_namelist = zf.namelist()
            for f_rel_path in zf_namelist:
                if f_rel_path.upper() == META_MANIFEST_REL_PATH:
                    manifest_path = f_rel_path
                    break
            if not manifest_path:
                print "Cannot find MANIFEST.MF file in: %s" % apk_path
                return None
            manifest_data = zf.read(manifest_path)
        
        mf = get_file_hashes_from_mf(manifest_data) #removing the header
        return mf
            


def get_file_hashes_from_mf(data):
    s = None #section separator
    if data.find("\r\r") > 0:
        s = "\r"
    elif data.find("\n\n") > 0:
        s = "\n"
    elif data.find("\r\n\r\n") > 0:
        s = "\r\n"
    
    mf_entries =  list()
    sections = data.split(s * 2)
    for sec in sections:
        d = dict(map(lambda z: (z[0], z[1]), filter(lambda y: len(y) == 2, map(lambda x: x.split(": ", 1), sec.replace(s + " ", "").split(s)))))
        if d.has_key(FILE_PATH_KEY):
            mf_entries.append(d)
    return mf_entries
            





def calculate_resources_similarity(out_file, in_dir, apk_pairs_file, scorerers, threads, timeout):
    field_names = ["apk1", "apk2", "result"]
    for sc in scorerers:
        field_names.extend(["%s_%s" % (sc.get_name(), RES_TYPE_NAMES[k]) for k in RES_TYPE_NAMES.keys()])
    
    in_queue = multiprocessing.JoinableQueue(IN_QUEUE_SIZE)
    out_queue = multiprocessing.JoinableQueue(OUT_QUEUE_SIZE)
    
    queue_populator = QueuePopulatorThread(in_queue, in_dir, apk_pairs_file)
    results_writer = FileWriterThread(out_queue, out_file, tuple(field_names))
    processor = ScorererProcessorPool(in_queue=in_queue, out_queue=out_queue, samples_directory=in_dir, scorerers=scorerers, threads=threads, timeout=timeout)
    
    queue_populator.start()
    processor.start_processes()
    results_writer.start()
    
    in_queue.join()    
    queue_populator.join()
    
    processor.stop_processes()
    
    out_queue.join()
    results_writer.stop_thread()
    results_writer.join()
         

def main(args):
    if not os.path.exists(args.in_dir):
        print "Directory with input apk files does not exist!!! Exiting!"
        return
    
    if not os.path.isdir(args.in_dir):
        print "Specified path is not a directory!!! Exiting!"
        return  
    
    if not args.out_file:
        print "Output file is not specified!!! Exiting!"
        return
    
    scorerers = None
    if args.all_metrics:
        scorerers = SimilarityScorerFactory.get_scorers()
    elif args.metrics:
        scorerers = SimilarityScorerFactory.get_scorers(args.metrics)
    else:
        print "Metrics are not provided!!!"
        return
    
    print "Starting analysis..."
    calculate_resources_similarity(out_file=args.out_file, in_dir=args.in_dir, 
            apk_pairs_file=args.pairs_file, scorerers=scorerers, 
            threads=args.threads_num, timeout=args.timeout)
    
    print "Done..."


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This application extracts similarity metrics of different types of files.')
    parser.add_argument('--threads', type=int, action='store', dest='threads_num', default=DEFAULT_PROCESSES_NUM,
        help="Number of parallel process to run for comparison")
    parser.add_argument('--timeout', type=int, action='store', dest='timeout', default=DEFAULT_TIMEOUT,
        help="Timeout after which the comparison process will be killed.")
    parser.add_argument('--pairs_file', action='store', dest='pairs_file', 
        help="Path to csv file with pairs of apps that are required to be compared.")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', dest="all_metrics", action='store_true', help="Calculate all available metrics")
    group.add_argument('-m', dest="metrics", metavar="METRIC", choices=SimilarityScorerFactory.SCORE_TYPES, action='append', help="Calculate metric. Can be added several metrics.")

    parser.add_argument('in_dir', help="Path to the folder with Android applications which are needed to be compared")
    parser.add_argument('out_file', help="Path to the output file to store the results")
    
    
#     print parser.print_help()
    args = parser.parse_args(["-m", "Jaccard", "/home/yury/tmp/apps_example/", "/home/yury/results.csv"])
    print args
#     args = parser.parse_args()
    main(args)
    
    