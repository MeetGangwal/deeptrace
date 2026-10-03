import torch
import platform

def test_apple_silicon_gpu():
    print(f"Python Platform: {platform.platform()}")
    print(f"PyTorch Version: {torch.__version__}")
    
    if torch.backends.mps.is_available():
        mps_device = torch.device("mps")
        print("\n✅ SUCCESS: Apple M5 GPU (MPS) is available and ready for deep learning!")
        
        x = torch.ones(5, device=mps_device)
        print(f"Test Tensor on GPU: {x}")
    else:
        print("\n❌ ERROR: MPS is not available. PyTorch will use the CPU.")

if __name__ == "__main__":
    test_apple_silicon_gpu()