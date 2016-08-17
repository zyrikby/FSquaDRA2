'''
Created on Mar 1, 2016

@author: Yury Zhauniarovich
'''
import math

class Block():
    name = "Block"
    
    def compare(self, list1, list2):
        if not list1 and not list2:
            return 1.0
        if not list1 or not list2:
            return 0.0
        
        return 1.0 - self.distance(list1, list2) / (len(list1) + len(list2))
    
    
    def distance(self, list1, list2):
        dict1 = dict()
        for k in list1:
            dict1[k] = dict1.get(k, 0) + 1
        dict2 = dict()
        for k in list2:
            dict2[k] = dict2.get(k, 0) + 1

        distance = 0.0
        elements_union = set(dict1.keys()).union(set(dict2.keys()))
        for elem in elements_union:
            distance += abs(dict1.get(elem, 0) - dict2.get(elem, 0))
        return float(distance)
    
    def get_name(self):
        return self.name


################################################################################


class Cosine():
    name = "Cosine"
    
    def compare(self, list1, list2):
        if not list1 and not list2:
            return 1.0
        if not list1 or not list2:
            return 0.0
        
        dict1 = dict()
        for k in list1:
            dict1[k] = dict1.get(k, 0) + 1
        dict2 = dict()
        for k in list2:
            dict2[k] = dict2.get(k, 0) + 1
        
        dot_product = 0.0
        magnitude1 = 0.0
        magnitude2 = 0.0
        elements_union = set(dict1.keys()).union(set(dict2.keys()))
        for elem in elements_union:
            count1 = dict1.get(elem, 0)
            count2 = dict2.get(elem, 0)
            
            dot_product += count1*count2
            magnitude1 += count1*count1 
            magnitude2 += count2*count2
        
        return dot_product / (math.sqrt(magnitude1) * math.sqrt(magnitude2))
        
    
    def distance(self, list1, list2):
        return (1.0 - self.compare(list1, list2))
    
    def get_name(self):
        return self.name


################################################################################


class Dice():
    name = "Dice"
    
    def compare(self, list1, list2):
        if not list1 and not list2:
            return 1.0
        if not list1 or not list2:
            return 0.0
        return ((2.0 * len(set(list1).intersection(list2))) / (len(list1) + len(list2))) 
    
    def distance(self, list1, list2):
        return (1.0 - self.compare(list1, list2))
    
    def get_name(self):
        return self.name


################################################################################


class Euclidian():
    name = "Euclidian"
    
    def compare(self, list1, list2):
        if not list1 and not list2:
            return 1.0
        
        max_distance = math.sqrt((len(list1)*len(list1) + len(list2)*len(list2)))        
        return (1.0 - (self.distance(list1, list2) / max_distance))
    
    
    def distance(self, list1, list2):
        dict1 = dict()
        for k in list1:
            dict1[k] = dict1.get(k, 0) + 1
        dict2 = dict()
        for k in list2:
            dict2[k] = dict2.get(k, 0) + 1
        
        distance = 0.0
        elements_union = set(dict1.keys()).union(set(dict2.keys()))
        for elem in elements_union:
            count1 = dict1.get(elem, 0)
            count2 = dict2.get(elem, 0)
            distance += ((count1 - count2)*(count1 - count2))
        
        return math.sqrt(distance)
            
            
    def get_name(self):
        return self.name
    
    
################################################################################


class GeneralizedJaccard():
    name = "GeneralizedJaccard"
    
    def compare(self, list1, list2):
        if not list1 and not list2:
            return 1.0
        if not list1 or not list2:
            return 0.0
        
        intersection = len(set(list1).intersection(set(list2)))
        return float(intersection) / (len(list1) + len(list2) - intersection)
    
    def distance(self, list1, list2):
        return (1.0 - self.compare(list1, list2))
            
            
    def get_name(self):
        return self.name
    
    
################################################################################


class GeneralizedOverlap():
    name = "GeneralizedOverlap"
    
    def compare(self, list1, list2):
        if not list1 and not list2:
            return 1.0
        if not list1 or not list2:
            return 0.0
        
        intersection = len(set(list1).intersection(set(list2)))
        return float(intersection) / min(len(list1), len(list2))
    
    def distance(self, list1, list2):
        raise NotApplicableException("Generalized Overlap cannot be used as a distance metric!")
            
    def get_name(self):
        return self.name
    
    
################################################################################


class Jaccard():
    name = "Jaccard"
    
    def compare(self, list1, list2):
        if not list1 and not list2:
            return 1.0
        if not list1 or not list2:
            return 0.0
        
        set1 = set(list1)
        set2 = set(list2)
        
        intersection = len(set1.intersection(set2))
        return float(intersection) / (len(set1) + len(set2) - intersection)
    
    def distance(self, list1, list2):
        return (1.0 - self.compare(list1, list2))
            
            
    def get_name(self):
        return self.name
    
    
################################################################################


class Overlap():
    name = "Overlap"
    
    def compare(self, list1, list2):
        if not list1 and not list2:
            return 1.0
        if not list1 or not list2:
            return 0.0
        
        set1 = set(list1)
        set2 = set(list2)
        
        intersection = len(set1.intersection(set2))
        return float(intersection) / min(len(set1), len(set2))
    
    def distance(self, list1, list2):
        return (1.0 - self.compare(list1, list2))
            
    def get_name(self):
        return self.name
    
    
################################################################################


class SimonWhite():
    name = "SimonWhite"
    
    def compare(self, list1, list2):
        if not list1 and not list2:
            return 1.0
        if not list1 or not list2:
            return 0.0
        
        intersection = len(set(list1).intersection(set(list2)))
        return (2.0 * intersection) / (len(list1) + len(list2))
    
    def distance(self, list1, list2):
        return (1.0 - self.compare(list1, list2))
            
    def get_name(self):
        return self.name
    
    
################################################################################


class Tanimoto():
    name = "Tanimoto"
    
    def compare(self, list1, list2):
        if not list1 and not list2:
            return 1.0
        if not list1 or not list2:
            return 0.0
        
        set1 = set(list1)
        set2 = set(list2)
        
        intersection = len(set1.intersection(set2))
        return float(intersection) / math.sqrt(len(set1) * len(set2))
    
    def distance(self, list1, list2):
        return (1.0 - self.compare(list1, list2))
            
    def get_name(self):
        return self.name
    
    
################################################################################



class NotApplicableException(Exception):
    pass


#******************************************************************************#
def block_test1():
    list1 =  "aaa bbb ccc ddd".split(' ')
    list2 = "aaa bbb ccc eee".split(' ')
    block_distance = Block()
    bd = block_distance.compare(list1, list2)
    assert bd == 0.75, "Error in block_test1. Actual value: %f" % bd
    
def block_test2():
    list1 = "aaa bbb".split(' ')
    list2 = "aaa aaa".split(' ')
    block_distance = Block()
    bd = block_distance.compare(list1, list2)
    assert bd == 0.5, "Error in block_test2. Actual value: %f" % bd

#******************************************************************************#

def cosine_test1():
    list1 = "aaa bbb ccc ddd".split(' ')
    list2 = "aaa bbb ccc eee".split(' ')
    cosine_similarity = Cosine()
    cs = cosine_similarity.compare(list1, list2)
    assert cs == 0.75, "Error in cosine_test1. Actual value: %f" % cs

def cosine_test2():
    list1 = "a b c d".split(' ')
    list2 = "a b e f".split(' ')
    cosine_similarity = Cosine()
    cs = cosine_similarity.compare(list1, list2)
    assert cs == 0.5, "Error in cosine_test2. Actual value: %f" % cs

#******************************************************************************#

def dice_test1():
    list1 = "aaa bbb ccc ddd".split(' ')
    list2 = "aaa bbb ccc eee".split(' ')
    dice_similarity = Dice()
    ds = dice_similarity.compare(list1, list2)
    assert ds == 0.75, "Error in dice_test1. Actual value: %f" % ds

def dice_test2():
    list1 = "a b c d".split(' ')
    list2 = "a b c e".split(' ')
    dice_similarity = Dice()
    ds = dice_similarity.compare(list1, list2)
    assert ds == 0.75, "Error in dice_test2. Actual value: %f" % ds

#******************************************************************************#

def euclidian_test1():
    list1 = "aaa bbb ccc ddd".split(' ')
    list2 = "aaa bbb ccc eee".split(' ')
    euclidian_similarity = Euclidian()
    es = euclidian_similarity.compare(list1, list2)
    assert es == 0.75, "Error in test1. Actual value: %f" % es

def euclidian_test2():
    list1 = "a b c d".split(' ')
    list2 = "a b c e".split(' ')
    euclidian_similarity = Euclidian()
    es = euclidian_similarity.compare(list1, list2)
    assert es == 0.75, "Error in test2. Actual value: %f" % es

#******************************************************************************#

def generalized_jaccard_test1():
    list1 = "aaa bbb ccc ddd".split(' ')
    list2 = "aaa bbb ccc eee".split(' ')
    generalized_jaccard_similarity = GeneralizedJaccard()
    res = generalized_jaccard_similarity.compare(list1, list2)
    assert res == 0.6, "Error in test1. Actual value: %f" % res

def generalized_jaccard_test2():
    list1 = "a b c".split(' ')
    list2 = "a b c e f g".split(' ')
    generalized_jaccard_similarity = GeneralizedJaccard()
    res = generalized_jaccard_similarity.compare(list1, list2)
    assert res == 0.5, "Error in test2. Actual value: %f" % res

#******************************************************************************#

def generalized_overlap_test1():
    list1 = "aaa bbb ccc ddd".split(' ')
    list2 = "aaa bbb ccc eee".split(' ')
    generalized_overlap_similarity = GeneralizedOverlap()
    res = generalized_overlap_similarity.compare(list1, list2)
    assert res == 0.75, "Error in test1. Actual value: %f" % res

def generalized_overlap_test2():
    list1 = "a b b c c".split(' ')
    list2 = "a b c e f g".split(' ')
    generalized_overlap_similarity = GeneralizedOverlap()
    res = generalized_overlap_similarity.compare(list1, list2)
    assert res == 0.6, "Error in test2. Actual value: %f" % res

#******************************************************************************#

def jaccard_test1():
    list1 = "aaa bbb ccc ddd".split(' ')
    list2 = "aaa bbb ccc eee".split(' ')
    jaccard_similarity = Jaccard()
    res = jaccard_similarity.compare(list1, list2)
    assert res == 0.6, "Error in test1. Actual value: %f" % res

def jaccard_test2():
    list1 = "a b b c c".split(' ')
    list2 = "a b c e f g".split(' ')
    accard_similarity = Jaccard()
    res = accard_similarity.compare(list1, list2)
    assert res == 0.5, "Error in test2. Actual value: %f" % res

#******************************************************************************#

def overlap_test1():
    list1 = "aaa bbb ccc ddd".split(' ')
    list2 = "aaa bbb ccc eee".split(' ')
    overlap_similarity = Overlap()
    res = overlap_similarity.compare(list1, list2)
    assert res == 0.75, "Error in test1. Actual value: %f" % res

def overlap_test2():
    list1 = "a b b c c".split(' ')
    list2 = "a b c e f g".split(' ')
    overlap_similarity = Overlap()
    res = overlap_similarity.compare(list1, list2)
    assert res == 1.0, "Error in test2. Actual value: %f" % res

#******************************************************************************#

def simon_white_test1():
    list1 = "aaa bbb ccc ddd".split(' ')
    list2 = "aaa bbb ccc eee".split(' ')
    simon_white_similarity = SimonWhite()
    res = simon_white_similarity.compare(list1, list2)
    assert res == 0.75, "Error in test1. Actual value: %f" % res

def simon_white_test2():
    list1 = "a b c d".split(' ')
    list2 = "a b c e".split(' ')
    simon_white_similarity = SimonWhite()
    res = simon_white_similarity.compare(list1, list2)
    assert res == 0.75, "Error in test2. Actual value: %f" % res

#******************************************************************************#
    
def tanimoto_test1():
    list1 = "aaa bbb ccc ddd".split(' ')
    list2 = "aaa bbb ccc eee".split(' ')
    tanimoto_similarity = Tanimoto()
    res = tanimoto_similarity.compare(list1, list2)
    assert res == 0.75, "Error in test1. Actual value: %f" % res

def tanimoto_test2():
    list1 = "aaa bbb ccc ddd aaa bbb ccc ddd".split(' ')
    list2 = "aaa bbb ccc eee".split(' ')
    tanimoto_similarity = Tanimoto()
    res = tanimoto_similarity.compare(list1, list2)
    assert res == 0.75, "Error in test2. Actual value: %f" % res

#******************************************************************************#



def test():
    #BlockTests
    block_test1()
    block_test2()
    
    #CosineTests
    cosine_test1()
    cosine_test2()
    
    #DiceTests
    dice_test1()
    dice_test2()
    
    #EuclidianTests
    euclidian_test1()
    euclidian_test2()
    
    #GeneralizedJaccardTests
    generalized_jaccard_test1()
    generalized_jaccard_test2()
    
    #GeneralizedOverlapTests
    generalized_overlap_test1()
    generalized_overlap_test2()
    
    #JaccardTests
    jaccard_test1()
    jaccard_test2()
    
    #OverlapTests
    overlap_test1()
    overlap_test2()
    
    #SimonWhiteTests
    simon_white_test1()
    simon_white_test2()
    
    #TanimotoTests
    tanimoto_test1()
    tanimoto_test2()
    
    
    
    
if __name__ == '__main__':
    test()