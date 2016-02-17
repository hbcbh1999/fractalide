{ stdenv, buildFractalideSubnet, upkeepers
  , web_server
  , ...}:

let
doc = import ../../doc {};
in
buildFractalideSubnet rec {
  src = ./.;
  subnet = ''
'path:(path="${doc}/share/doc/fractalide/manual.html")' -> www_dir www(${web_server})
'domain_port:(domainPort="localhost:8083")' -> domain_port www()
'url:(url="/docs")' -> url www()
  '';

  meta = with stdenv.lib; {
    description = "Subnet: Fractalide manual";
    homepage = https://github.com/fractalide/fractalide/tree/master/components/docs;
    license = with licenses; [ mpl20 ];
    maintainers = with upkeepers; [ dmichiels sjmackenzie];
  };
}
