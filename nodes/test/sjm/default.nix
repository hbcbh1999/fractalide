{ subgraph, nodes, edges }:

subgraph {
 src = ./.;
 flowscript = with nodes; with edges; ''
  '${maths_boolean}:(boolean=true)' -> a nand(${maths_boolean_nand}) output -> input io_print(${maths_boolean_print})
  '${maths_boolean}:(boolean=true)' -> b nand()
 '';
}
