/// <reference path="./.sst/platform/config.d.ts" />

export default $config({
  app(input) {
    return {
      name: "fastapi-poc",
      removal: input?.stage === "production" ? "retain" : "remove",
      protect: ["production"].includes(input?.stage),
      home: "aws",
    };
  },

  async run() {

    // Create a DynamoDB table with a primary index and a global secondary index
    const table = new sst.aws.Dynamo("Tasks", {
      fields: {
        taskId: "string",
        userId: "string",
        createdAt: "number",
      },
      primaryIndex: { hashKey: "taskId"},
      globalIndexes: {
        userIdIndex: { hashKey: "userId", rangeKey: "createdAt" }
      }
    });

    // Create a Lambda function with a URL
    // and link it to the DynamoDB table
    // This function will be triggered by HTTP requests
    const api = new sst.aws.Function("FastAPIPOC", {
      handler: "functions/src/functions/main.handler",
      runtime: "python3.11",
      url: true,
      link: [table],
      environment: {
        TABLE_NAME: table.name,
      }
    });

    // Export the API URL and table name
    return {
      api: api.url,
      table: table.name,
    };


  },
});
