{ edge, edges }:

edge {
  src = ./.;
  edges =  with edges; [];
  schema = with edges; ''
    @0xcd25af61b5d6c76b;

    struct GenericU64 {
            number @0 :UInt64;
    }
  '';
}
