{ subgraph, nodes, edges }:

let
  doc = import ../../doc {};
in
subnet  {
  src = ./.;
  flowscript = with nodes; with edges; ''
  '${path}:(path="${doc}/share/doc/fractalide/")' -> www_dir www(${web_server})
  '${domain_port}:(domainPort="localhost:8083")' -> domain_port www()
  '${url}:(url="/docs")' -> url www()
  '${generic_text}:(text="[*] serving: localhost:8083/docs/manual.html")' -> input disp(${io_print})
  '';
}
