import os
import pickle


class DataSerializer:
    # Save the data for easy access
    @staticmethod
    def save_data(
            data,
            pickle_file,
            overwrite=False
    ):
        os.makedirs(os.path.dirname(pickle_file), exist_ok=True)
        if overwrite or not os.path.isfile(pickle_file):
            print('Saving data to pickle file...')
            try:
                with open(pickle_file, 'wb') as pfile:
                    pickle.dump(
                        data,
                        pfile, pickle.HIGHEST_PROTOCOL)
            except Exception as e:
                print('Unable to save data to', pickle_file, ':', e)
                raise
        else:
            print('WARNING: {} already exists.'.format(pickle_file))

        print('Data cached in pickle file.')

    @staticmethod
    def reload_data(pickle_file):
        pickle_data = None
        if os.path.isfile(pickle_file):
            with open(pickle_file, 'rb') as f:
                pickle_data = pickle.load(f)
            print('Data loaded from pickle file.')
        return pickle_data
