document.addEventListener('DOMContentLoaded', function() {
    function exibirMensagem(mensagem, tipo) {
        const mensagemDiv = document.getElementById('mensagem');
        mensagemDiv.textContent = mensagem;
        mensagemDiv.className = `mensagem ${tipo}`;
    }

    const formSaque = document.querySelector('form[action^="/saque"]');
    if (formSaque) {
        formSaque.addEventListener('submit', function(event) {
            event.preventDefault();
            const valorSaque = document.getElementById('valor_saque').value;
            const numeroConta = '{{ numero_da_conta }}';

            // Enviar solicitação AJAX para obter saldo atual
            fetch(`/saldo/${numeroConta}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Erro ao obter saldo');
                    }
                    return response.json();
                })
                .then(data => {
                    const saldoAtual = data.saldo;
                    if (parseFloat(valorSaque) > saldoAtual) {
                        exibirMensagem('Saldo insuficiente para realizar o saque.', 'erro');
                    } else {
                        exibirMensagem(`Saque de R$ ${valorSaque} realizado com sucesso.`, 'sucesso');
                    }
                })
                .catch(error => {
                    console.error('Erro:', error);
                    exibirMensagem('Erro ao obter saldo.', 'erro');
                });

            document.getElementById('valor_saque').value = '';
        });
    }
});

