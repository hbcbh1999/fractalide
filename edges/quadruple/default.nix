{ edge, edges }:

edge {
  src = ./.;
  edges =  with edges; [];
  schema = with edges; ''
    @0xcfac55e5d5e97b4f;

    struct Quadruple {
      first @0 : UInt32;
      second @1 : UInt32;
      third @2 : UInt32;
      fourth @3 : Float32;
    }
  '';
}
