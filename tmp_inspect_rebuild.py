from embeddings import rebuild_index_from_dataset, load_index
from recognition import recognize_face
import os

print('PWD:', os.getcwd())
count = rebuild_index_from_dataset('dataset')
print('Rebuilt entries:', count)
index, labels = load_index()
print('Index present:', index is not None)
print('Labels count:', None if labels is None else len(labels))
if labels is not None:
    print('Labels sample:', labels[:10])

res = recognize_face('samples/a.jpg', resize_to=(320,240))
print('Recognition result:', res)
