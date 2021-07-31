// initialized sdk and exported configuration as parameters
async function sdkSetup(sdk, configuration) {
  const parsedConfiguration = typeof configuration === 'string' ? JSON.parse(configuration) : configuration
  const globalConfiguration = parsedConfiguration.find(({ id }) => id === 'global')
  const addressConfigurations = parsedConfiguration.filter(({ id }) => id !== 'global')

  // save global configuration first and wait for it to be saved
  globalConfiguration && await sdk.configuration({scope: 'global', filters: globalConfiguration.filters})

  addressConfigurations.forEach(({id, filters, abi}) => {
    const abiObj = abi ? { abi } : {}
    sdk.configuration({...abiObj, filters, scope: id, watchAddress: true})
  })

}

export default sdkSetup