// For Node >= v13 / es module environments
import BlocknativeSdk from 'bnc-sdk'
import Web3 from 'web3'


import WebSocket from 'ws' // only neccessary in server environments

// create options object
const options = {
  dappId: 'Your dappId here',
  networkId: 1,
  system: 'bitcoin', // optional, defaults to ethereum
  transactionHandlers: [event => console.log(event.transaction)],
  ws: WebSocket, // only neccessary in server environments 
  name: 'Instance name here', // optional, use when running multiple instances
  onerror: (error) => {console.log(error)} //optional, use to catch errors
}

// initialize and connect to the api
const blocknative = new BlocknativeSdk(options)

// initialize web3
const web3 = new Web3(window.ethereum)

// get current account
const accounts = await web3.eth.getAccounts();
const address = accounts[0];

// create transaction options object
const txOptions = {
  from: address,
  to: "0x792ec62e6840bFcCEa00c669521F678CE1236705",
  value: "1000000"
}

// initiate a transaction via web3.js
web3.eth.sendTransaction(txOptions).on('transactionHash', hash => {
  // call with the transaction hash of the
  // transaction that you would like to receive status updates for
  const { emitter } = blocknative.transaction(hash)

  // listen to some events
  emitter.on('txPool', transaction => {
    console.log(`Sending ${transaction.value} wei to ${transaction.to}`)
  })

  emitter.on('txConfirmed', transaction => {
    console.log('Transaction is confirmed!')
  })

  // catch every other event that occurs and log it
  emitter.on('all', transaction => {
    console.log(`Transaction event: ${transaction.eventCode}`)
  })
})