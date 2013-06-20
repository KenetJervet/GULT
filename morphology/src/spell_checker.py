#!/usr/bin/python

#######################################################
# Group-wide universal language word spelling checker #
# Author: Kenet Jervet                                #
# Date: 2013/06/13                                    #
#                                                     #
# Version: 0.3.1-build0312                            #
#                                                     #  
# Copyright 2013 Kenet Jervet & Desmond Lee           #
#######################################################
    

import sys

class _Stati():
    Error = -1  # 错误
    Unknown = 0  # 未知
    Vowel = 100  # 元音
    Monophthong = 101 # 单元音
    Diphthong = 102  # 双元音 
    Triphthong = 103 # 三元音
    Consonant = 200  # 辅音
    Pure_Consonant = 201  # 不知道叫神马
    Liquid = 202  # 流音
    Glide = 203  # 介音
    End = 65535  # 结束
    
    @classmethod
    def is_a(cls, stati, test_stati):
        '''
        检查test_stati类别是否包含stati类别
        
        参数:
        stati -- 待测源类别
        test_stati -- 待测目标类别 
        '''
        if test_stati % 100 == 0:
            if 0 <= stati - test_stati < 100:
                return True
        else:
            if stati == test_stati:
                return True
        
        return False
    
    @classmethod
    def is_any_of(cls, stati, *test_statis):
        '''
        检查stati类别是否被test_statis中的任意一个类别包含
        '''
        return True if len([x for x in test_statis if _Stati.is_a(stati, x)]) > 0 else False

voices = {
    _Stati.Monophthong: ['a', 'e', 'i', 'o', 'u', 'eu'],
    _Stati.Diphthong: ['ia', 'ie', 'io', 'iu', 'ua', 'ue', 'ui', 'uo', 'ai', 'ei', 'oi', 'au', 'ou'],
    _Stati.Pure_Consonant: ['p', 'f', 'm', 'b', 'v', 'th', 'dh', 't', 'n', 'd', 's', 'z', 'sh', 'zh', 'c', 'j', 'ch', 'jh', 'k', 'ng', 'g', 'h', 'w', 'y'],
    _Stati.Liquid: ['l', 'r'],
    _Stati.Glide: []
}


class Word:
    voices_expanded = [(key, value) for key in voices for value in voices[key]]  # 展开为二元组

    def __init__(self, word):
        
        # 判断一下参数是否为字符串
        if not isinstance(word, str):
            raise TypeError

        self.word = word  # 存单词
        self.word_len = len(word)  # 存拼写

    def is_valid(self):
        '''
        检查拼写
        '''
        class Cloj():
            '''
            储存闭包数据
            '''
            slices = []  # 已拆出来的切片
            next_index = 0  # 下一个待拆点
            consonant_seq_length = 0  # 已记载连续辅音数
            total_phonemes = 0  # 总音位数
            syllables = 0  # 总音节数
            
            def copy(self):
                '''
                复制
                '''
                x = Cloj()
                x.slices = self.slices[:]
                x.next_index = self.next_index
                x.consonant_seq_length = self.consonant_seq_length
                x.total_phonemes = self.total_phonemes
                x.syllables = self.syllables
                return x
        
        def __aspire(index):
            if index > self.word_len - 1:
                return [((_Stati.End, ''), None)]

            current_slice = ''
            cands = self.voices_expanded
            res = []
            while True:  
                current_slice += self.word[index]
                
                for cand in [x for x in cands if x[1] == current_slice]:
                    res.append((cand, index + 1))
                    
                cands = [x for x in cands if x[1].startswith(current_slice) and x[1] != current_slice]
                
                if len(cands) == 0:
                    break
                
                index += 1
                if index > self.word_len - 1:
                    break
                
            return res

        def __save_status(cloj, aslice, next_index):
            
            cloj.slices.append(aslice)
            cloj.next_index = next_index

        def __do_vowel(cloj):
            
            if len(cloj.slices) > 1 and not _Stati.is_any_of(cloj.slices[-2][0], _Stati.Consonant):
                return False

            cloj.consonant_seq_length = 0  # Reset
            
            cloj.syllables += 1
            
        def __do_monophthong(cloj):
            return __do_vowel(cloj)
            
        def __do_diphthong(cloj):
            if len(cloj.slices) > 1:
                if not _Stati.is_any_of(cloj.slices[-2][0], _Stati.Consonant) and cloj.slices[-2][1] not in ['i', 'u']: 
                    return False

            cloj.consonant_seq_length = 0  # Reset
            
            cloj.syllables += 1
        
        def __do_triphthong(cloj):
            return __do_vowel(cloj)

        def __do_pure_consonant(cloj):
            
            if cloj.consonant_seq_length > 1:
                return False

            if len(cloj.slices) > 1:
                if cloj.slices[-1][1] == cloj.slices[-2][1]:
                    return False
                
                if not _Stati.is_any_of(cloj.slices[-2][0], _Stati.Pure_Consonant, _Stati.Vowel):
                    return False
            
            cloj.consonant_seq_length += 1

        def __do_liquid(cloj):
            
            if cloj.consonant_seq_length > 2:
                return False
            
            if len(cloj.slices) > 1:
                if cloj.slices[-1][1] == cloj.slices[-2][1]:
                    return False
            
            _consonant_seq_length = 0
            
        def __do_glide(cloj):
            
            if len(cloj.slices) > 1 and not _Stati.is_any_of(cloj.slices[-2][0], _Stati.Vowel, _Stati.Consonant):
                return False
            
            _consonant_seq_length = 0

        def __do_end(cloj):
            
            if cloj.syllables == 0:
                return False
            
            if _Stati.is_any_of(cloj.slices[-2][0], _Stati.Liquid, ):
                if _Stati.is_any_of(cloj.slices[-3][0], _Stati.Consonant):
                    return False
                
            if _Stati.is_any_of(cloj.slices[-2][0], _Stati.Glide, ):
                return False
            
            return True

        def recurse(cloj):
            _new_slices = __aspire(cloj.next_index)
            
            _new_slices.reverse()
            
            for aslice in _new_slices:
                new_cloj = cloj.copy()
                __save_status(new_cloj, aslice[0], aslice[1])
                slice_valid = {
                    _Stati.Monophthong : lambda: __do_vowel(new_cloj),
                    _Stati.Diphthong : lambda: __do_diphthong(new_cloj),
                    _Stati.Triphthong : lambda: __do_triphthong(new_cloj),
                    _Stati.Pure_Consonant : lambda: __do_pure_consonant(new_cloj),
                    _Stati.Liquid : lambda: __do_liquid(new_cloj),
                    _Stati.Glide: lambda: __do_glide(new_cloj),
                    _Stati.Error : lambda: False,
                    _Stati.End : lambda: __do_end(new_cloj)
                }[aslice[0][0]]()

                if slice_valid == False:
                    continue
                elif slice_valid == True:
                    print([x[1] for x in new_cloj.slices][:-1])
                    return True
                else:
                    if recurse(new_cloj):
                        return True
                    
                    
            return False
          
        cloj = Cloj()          
        return recurse(cloj)
                
                

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: %s [word1, [word2, ...]]" % __file__)
        
    final = True

    for aword in sys.argv[1:]:
        word = Word(aword)
        is_valid = word.is_valid()
        if is_valid:
            result = "OK."
        else:
            result = "Bad."
        print("%s: %s" % (aword, result))
        sys.exit(0 if is_valid else 1)
    
