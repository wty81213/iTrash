import unicodedata
import numpy as np 
import torch 
from tqdm import tqdm
from transformers import BertTokenizer
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import Dataset

def full2half(text:str) -> str:
    return unicodedata.normalize("NFKC",text)

class IntentionDataset(Dataset) :

    def __init__(self, dataset, token_path, maxlen=512):          
        
        self.sentences,self.l1_target, self.target = dataset
        self.total_cnt = len(self.sentences)

        if self.target is None:
            self.l1_target = [0]*self.total_cnt 
            self.target = [0]*self.total_cnt 

        assert len(self.sentences) ==  len(self.target)
        
        self.tokenizer = BertTokenizer.from_pretrained(token_path)
        self.sentences = self.text_preparation(self.sentences)
        self.sentences_ids = self.convert2idx(self.sentences)

        self.maxlen = maxlen

    def text_preparation(self, sentences):

        pbar = tqdm(sentences)
        pbar.set_description('text_preparation')
        
        ouptut_sentences = []
        for s in pbar :
            s = full2half(s)
            s = s.lower()
            ouptut_sentences.append(s)

        return ouptut_sentences       

    def convert2idx(self, sentences):
        
        pbar = tqdm(sentences)
        pbar.set_description('convert2idx')

        sentences_ids = []
        for s in pbar:
            sentence_ids = self.tokenizer.convert_tokens_to_ids(list(s))
            sentence_ids = [101] + sentence_ids + [102]

            sentences_ids.append(sentence_ids)
        
        return sentences_ids

    def __len__(self):
        return self.total_cnt

    def __getitem__(self, idx):

        return self.sentences[idx],\
               torch.tensor(self.sentences_ids[idx]), \
               torch.tensor(self.l1_target[idx]),\
               torch.tensor(self.target[idx])
                

    def collate_fn(self, batch):
        
        sentences, sentences_ids, l1_target, target = zip(*batch)
        l1_target = torch.stack(l1_target).long()
        target = torch.stack(target).long()
            
        sentences_len = [len(s) for s in sentences_ids]
        sentences_ids = pad_sequence(sentences_ids, batch_first = True)
        
        position_ids = []
        attention_mask = []
        token_type_ids = []
        for l in sentences_len:
            position_ids.append(torch.arange(0,l))
            attention_mask.append(torch.ones(l))
            token_type_ids.append(torch.zeros(l))

        sentences_ids = pad_sequence(sentences_ids, batch_first = True)
        position_ids = pad_sequence(position_ids, batch_first = True)
        attention_mask = pad_sequence(attention_mask, batch_first = True)
        token_type_ids = pad_sequence(token_type_ids, batch_first = True)
                
        if sentences_ids.shape[1] > self.maxlen:
            sentences_ids = sentences_ids[:,:self.maxlen]
            attention_mask = attention_mask[:,:self.maxlen]
            position_ids = position_ids[:,:self.maxlen]
            token_type_ids = token_type_ids[:,:self.maxlen]
        
        data = {'input_ids':sentences_ids.long(),
                'token_type_ids':token_type_ids.long(),
                'attention_mask':attention_mask.long(),
                'position_ids':position_ids.long()}
        
        return sentences,data,target