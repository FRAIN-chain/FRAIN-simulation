require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.6.12",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
    },
  },
  paths: {
    sources: './benchmark',
  },
  defaultNetwork: 'wemixTest',
  networks: {
    hardhat: {},
    wemixTest: {
      url: 'https://api.test.wemix.com',
    },
  },
};
