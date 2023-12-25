import os
from copy import copy
from typing import Union

import numpy as np
import pandas as pd
from sklearn import model_selection
from torcheeg.datasets.module.base_dataset import BaseDataset


def train_test_split(dataset: BaseDataset,
                     test_size: float = 0.2,
                     shuffle: bool = False,
                     random_state: Union[float, None] = None,
                     split_path: str = '.torcheeg/split/train_test_split'):
    r'''
    A tool function for cross-validations, to divide the training set and the test set. It is suitable for experiments with large dataset volume and no need to use k-fold cross-validations. The test samples are sampled according to a certain proportion, and other samples are used as training samples. In most literatures, 20% of the data are sampled for testing.

    :obj:`train_test_split` devides the training set and the test set without grouping. It means that during random sampling, adjacent signal samples may be assigned to the training set and the test set, respectively. When random sampling is not used, some subjects are not included in the training set. If you think these situations shouldn't happen, consider using :obj:`train_test_split_per_subject_groupby_trial` or :obj:`train_test_split_groupby_trial`.

    .. image:: _static/train_test_split.png
        :alt: The schematic diagram of train_test_split
        :align: center

    |

    .. code-block:: python

        dataset = DEAPDataset(io_path=f'./deap',
                              root_path='./data_preprocessed_python',
                              online_transform=transforms.Compose([
                                  transforms.To2d(),
                                  transforms.ToTensor()
                              ]),
                              label_transform=transforms.Compose([
                                  transforms.Select(['valence', 'arousal']),
                                  transforms.Binary(5.0),
                                  transforms.BinariesToCategory()
                              ]))

        train_dataset, test_dataset = train_test_split(dataset=dataset, split_path='./split')

        train_loader = DataLoader(train_dataset)
        test_loader = DataLoader(test_dataset)
        ...

    Args:
        dataset (BaseDataset): Dataset to be divided.
        test_size (int):  If float, should be between 0.0 and 1.0 and represent the proportion of the dataset to include in the test split. If int, represents the absolute number of test samples. (default: :obj:`0.2`)
        shuffle (bool): Whether to shuffle the data before splitting into batches. Note that the samples within each split will not be shuffled. (default: :obj:`False`)
        random_state (int, optional): When shuffle is :obj:`True`, :obj:`random_state` affects the ordering of the indices, which controls the randomness of each fold. Otherwise, this parameter has no effect. (default: :obj:`None`)
        split_path (str): The path to data partition information. If the path exists, read the existing partition from the path. If the path does not exist, the current division method will be saved for next use. (default: :obj:`./split/k_fold_dataset`)
    '''
    if not os.path.exists(split_path):
        os.makedirs(split_path)
        info = dataset.info

        n_samples = len(dataset)
        indices = np.arange(n_samples)
        train_index, test_index = model_selection.train_test_split(
            indices,
            test_size=test_size,
            random_state=random_state,
            shuffle=shuffle)
        train_info = info.iloc[train_index]
        test_info = info.iloc[test_index]

        train_info.to_csv(os.path.join(split_path, 'train.csv'), index=False)
        test_info.to_csv(os.path.join(split_path, 'test.csv'), index=False)

    train_info = pd.read_csv(os.path.join(split_path, 'train.csv'))
    test_info = pd.read_csv(os.path.join(split_path, 'test.csv'))

    train_dataset = copy(dataset)
    train_dataset.info = train_info

    test_dataset = copy(dataset)
    test_dataset.info = test_info

    return train_dataset, test_dataset
