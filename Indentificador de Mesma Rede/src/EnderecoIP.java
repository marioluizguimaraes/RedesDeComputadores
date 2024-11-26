import java.util.Arrays;

public class EnderecoIP {
    private String enderecoIp;
    private String mascaraDeRede;

    private String[] binarioCodeIp = new String[4];
    private String[] binarioCodeMascara = new String[4];

    public EnderecoIP (String ip, String mascara){
        enderecoIp = ip;
        mascaraDeRede = mascara;

        String[] StringDeOctetosDeIp = this.enderecoIp.split("\\.");
        String[] StringDeOctetosDeMascara = this.mascaraDeRede.split("\\.");

        int[] octetosDeIp = Arrays.stream(StringDeOctetosDeIp).mapToInt(Integer::parseInt).toArray();
        int[] octetosDeMascara = Arrays.stream(StringDeOctetosDeMascara).mapToInt(Integer::parseInt).toArray();

        //----------------------------------------------------------------------------------------------------------------

        for (int i = 0; i < 4; i++) {
            binarioCodeIp[i] = String.format("%08d", Integer.parseInt(Integer.toBinaryString(octetosDeIp[i])));
            binarioCodeMascara[i] = String.format("%08d", Integer.parseInt(Integer.toBinaryString(octetosDeMascara[i])));
        }
    }

    private String inverterBits(String mascarabinario) {
        StringBuilder invertido = new StringBuilder();
        for (char bit : mascarabinario.toCharArray()) {
            invertido.append(bit == '0' ? '1' : '0'); // Inverte 0 para 1 e 1 para 0
        }
        return invertido.toString();
    }

    public String broadcastDaRede(String mascarabinario){

        String mascaraInvertida  = this.inverterBits(mascarabinario);
        StringBuilder ipDeBroadcast = new StringBuilder();

        char[] mascaraBit = mascaraInvertida.toCharArray();
        char[] ipBit = getIp().toCharArray();

        for (int i = 0; i < mascaraBit.length; i++ ) {
            if ( mascaraBit[i] == '0'){
                 ipDeBroadcast.append(ipBit[i]);
            }
            else if (mascaraBit[i] == '.') {
                ipDeBroadcast.append('.');
            }
            else {
                ipDeBroadcast.append(mascaraBit[i]);
            }
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
