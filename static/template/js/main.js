$('.btn-delete').click(function() {
    let that = $(this);
    Swal.fire({
        title: 'Konfirmasi Hapus',
        text: "Apakah anda yakin ingin menghapus?",
        showCancelButton: true,
        customClass: 'swal-wide',

        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Hapus',
        cancelButtonText: 'Batal',
    }).then((result) => {
        if (result.value) {
            Swal.fire(
                'Dihapus!',
                'Berhasil menghapus data.',
                'success'
                );
            that.parent('form').submit();
        }
    })
})