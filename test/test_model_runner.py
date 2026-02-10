from pyqualw2 import model_runner

def test_model_runner():
    test_run = model_runner.ModelRunner([1,2,3])
    test_run.run()
    print('hello')

if __name__ == "__main__":
    test_model_runner()