const { expect } = require("chai");

const data = require("./inputs.json");

describe("CommitReveal", function () {
  let signer = {
    "tester": null
  };
  let contract = {
    "commitReveal": null
  };

  async function set(verbose = true) {
    [signer.tester] = await ethers.getSigners();

    let balanceOfTestter = await signer.tester.getBalance() / (10 ** 18);
    console.log("Tester:\t", signer.tester.address, `(${balanceOfTestter} ETH)`);
  }

  async function deploy() {
    process.stdout.write("Deploy CommitReveal");
    const CommitReveal = await ethers.getContractFactory("CommitReveal", signer.tester);
    contract.commitReveal = await CommitReveal.deploy();
    await contract.commitReveal.deployed();
    console.log(":\t", contract.commitReveal.address);
  }

  round = 0;
  temp_round = round;

  describe("Normal", function () {
    it("Commit Hash", async function () {
      await set();
      await deploy();

      for (d of data) {
        input = await contract.commitReveal.stringToBytes(d);

        let txRes = await contract.commitReveal.commit(
          input,
          950327,
          round
        );
        await txRes.wait();

        round += 1;
      }
    });
    it("Reveal Hash", async function () {
      for (d of data) {
        input = await contract.commitReveal.stringToBytes(d);

        let txRes = await contract.commitReveal.reveal(
          input,
          signer.tester.address,
          950327,
          temp_round
        );
        await txRes.wait();

        await contract.commitReveal.saved_commits(temp_round, signer.tester.address);
        expect(txRes).to.equal(txRes);

        temp_round += 1;
      }
    });
  });

  temp_round = round;

  describe("Hashed", function () {
    it("Commit Hash", async function () {
      // await set();
      // await deploy();

      for (d of data) {
        input = await contract.commitReveal.stringToBytes(d);
        hashed_input = await contract.commitReveal.hashString(input);

        let txRes = await contract.commitReveal.commit_hashed(
          hashed_input,
          950327,
          round
        );
        await txRes.wait();

        round += 1;
      }
    });
    it("Reveal Hash", async function () {
      for (d of data) {
        input = await contract.commitReveal.stringToBytes(d);
        hashed_input = await contract.commitReveal.hashString(input);

        let txRes = await contract.commitReveal.reveal_hashed(
          hashed_input,
          signer.tester.address,
          950327,
          temp_round
        );
        await txRes.wait();

        await contract.commitReveal.saved_commits(temp_round, signer.tester.address);
        expect(txRes).to.equal(txRes);

        temp_round += 1;
      }
    });
  });
});
