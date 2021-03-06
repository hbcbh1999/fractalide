{ agent, edges, crates, pkgs }:

agent {
  src = ./.;
  edges = with edges; [ fbp_graph path option_path ];
  crates = with crates; [ rustfbp capnp ];
  osdeps = with pkgs; [];
  depsSha256 = "1g46ac4gqf45c567fgf8hrdpdhgd8hq0vpcnz68q1jf0hgggg3kw";
}
