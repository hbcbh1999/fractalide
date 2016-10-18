{ stdenv, buildFractalideComponent, genName, upkeepers
  , maths_number
  , ...}:

buildFractalideComponent rec {
  name = genName ./.;
  src = ./.;
  contracts = [ maths_number ];
  depsSha256 = "0ifckp6zp13xb4lr1vs2jrbwafw2k0id40b18mfdchnlh8dj3bpk";

  meta = with stdenv.lib; {
    description = "Component: Adds all inputs together";
    homepage = https://github.com/fractalide/fractalide/tree/master/components/maths/add;
    license = with licenses; [ mpl20 ];
    maintainers = with upkeepers; [ dmichiels sjmackenzie];
  };
}
