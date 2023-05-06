const provider = new ethers.providers.JsonRpcProvider("https://api.test.wemix.com/");
// const provider = new ethers.providers.JsonRpcProvider("http://localhost:8545/");
const deployer = new ethers.Wallet("10011001100110011001bc02b5890c4cdbde7419031d03270327032703270327", provider);

GAS_PRICE = 110 * (10 ** 9);
SETTINGS = { gasPrice: GAS_PRICE, value: 0 };

async function main() {
    console.log(`Deployer: ${deployer.address}`);

    // deploy
    const VRF = await ethers.getContractFactory("VRFGasHelper");
    const vrf = await VRF.connect(deployer).deploy(SETTINGS);
    console.log(`Deploy tokenA: ${vrf.address}`);
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit("1");
    });
