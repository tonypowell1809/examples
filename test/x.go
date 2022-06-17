package test

import (
"fmt"
"strconv"
"testing"

"github.com/gruntwork-io/terratest/modules/terraform"
"github.com/stretchr/testify/assert"
)

func checkCount(output string, count int, opts *terraform.Options, t *testing.T) {
/*
This function will output an integer from Terraform and see if it equals expected int
*/
CountOutput := terraform.Output(t, opts, output)
fmtCountOutput := fmt.Sprintf("%s", CountOutput)
outCount, _ := strconv.Atoi(fmtCountOutput)
assert.Equal(t, count, outCount)
}

func checkIncludes(output string, item string, opts *terraform.Options, t *testing.T) bool {
/*
This function will output a list from Terraform and look for an item in the list
*/
listOutput := terraform.OutputList(t, opts, output)
for _, b := range listOutput {
if b == item {
return true
}
}
return false
}

func getListCount(output string, opts *terraform.Options, t *testing.T) int {
listOutput := terraform.OutputList(t, opts, output)
return len(listOutput)
}
