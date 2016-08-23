# FSquaDRA 2 
Evaluation of Resource-based App Repackaging Detection in Android


## Description
This work is a [continuation](https://github.com/zyrikby/FSquaDRA) of the exploration of resource-based app repackaging detection in Android. 

Here we developed a tool that compares pairs of Android applications taking into account different metrics and different types of files constituting Android package.


## Publication
The results of our research will be presented at the [21st Nordic Conference on Secure IT Systems](http://nordsec.oulu.fi/). Please, use the following bibtex reference to cite our paper:
```
@inproceedings{EvaluationOfResourceBasedAppRepackagingDetection_Gadyatskaya2016,
    author = {Gadyatskaya, Olga and Lezza, Andra-Lidia and Zhauniarovich, Yury},
    title = {{Evaluation of Resource-based App Repackaging Detection in Android}},
    booktitle = {Proceedings of the 21st Nordic Conference on Secure IT Systems},
    series = {NordSec 2016},
    pages = {to appear},
    year = {2016},
}
```

## Repository Structure
The repository has two main files:
 * metrics.py - this is a library that provides different similarity metrics. It is a Python port of a part of Java [SimMetrics](https://github.com/Simmetrics/simmetrics) library.
 * resource_score_extractor.py - is the main program that is able to compute different similarity scores on files constituting Android package. It exploits the metrics.py library to compute similarity scores.  


## Usage
The tool is written using Python 2.7 and tested on Kubuntu 16.04 operating system. Run `python resource_score_extractor.py -h` to see the program help.
