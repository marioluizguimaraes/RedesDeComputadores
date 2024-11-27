import java.util.Arrays;

public class EnderecoIP {

    private String enderecoIp;
    private String mascaraDeRede;
    private String[] binarioCodeIp;
    private String[] binarioCodeMascara;

    public EnderecoIP (String ip, String mascara){
        this.enderecoIp = ip;
        this.mascaraDeRede = mascara;
        this.binarioCodeIp = new String[4];
        this.binarioCodeMascara = new String[4];

        for (int i = 0; i < 4; i++) {
            this.binarioCodeIp[i] = String.format("%08d", Integer.parseInt(Integer.toBinaryString(this.OctetosEmInt(this.enderecoIp)[i])));
            this.binarioCodeMascara[i] = String.format("%08d", Integer.parseInt(Integer.toBinaryString(this.OctetosEmInt(this.mascaraDeRede)[i])));
        }
    }

    private String[] OctetosEmstring(String endereco){
        return endereco.split("\\.");
    }

    private int[] OctetosEmInt (String endereco){
        return Arrays.stream(this.OctetosEmstring(endereco)).mapToInt(Integer::parseInt).toArray();
    }


    private String inverterBits(String mascarabinario) {
        StringBuilder invertido = new StringBuilder();
        for (char bit : mascarabinario.toCharArray()) {
            invertido.append(bit == '0' ? '1' : '0');
        }
        return invertido.toString();
    }

    public String broadcastDaRede(String mascarabinario){

        String mascaraInvertida  = this.inverterBits(mascarabinario);
        StringBuilder ipDeBroadcast = new StringBuilder();

        char[] mascaraBit = mascaraInvertida.toCharArray();
        char[] ipBit = getIp().toCharArray();

        for (int i = 0; i < mascaraBit.length; i++ ) {
            var a = switch(mascaraBit[i]) {
                case '0' -> ipBit[i];
                case '.' -> '.';
                default ->  mascaraBit[i];
            };
            ipDeBroadcast.append(a);
        }
        return ipDeBroadcast.toString();
    }

    public String getIp(){
        return String.join(".", binarioCodeIp);
    }

    public String getMascara(){
        return String.join(".", binarioCodeMascara);
    }

}
