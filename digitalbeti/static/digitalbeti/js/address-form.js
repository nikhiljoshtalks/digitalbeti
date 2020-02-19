$(document).ready(() => {
    console.log('document ready');
    $('#id_permanent-state').on('change', (e) => {
            let state_name = e.target.value;
            $.ajax({
                method: "POST",
                url: "/api/vd/districts",
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify({'state': state_name})
            }).then(data => {
                console.log(data);
                //Populate the district drop down
                let option = '';
                const stateLen = data.districts.length;
                console.log(stateLen);
                $('#id_permanent-district').empty();
                $('#id_permanent-subdistrict').empty();
                $('#id_permanent-village').empty();
                for (var i = 0; i < stateLen; i++) {
                    console.log(data.districts[i]);
                    option = '<option value="' + data.districts[i] + '">' + data.districts[i] + '</option>';
                    $('#id_permanent-district').append(option);

                }
            })
        }
    );
    $('#id_permanent-district').on('change', (e) => {
            state_name = $('#id_permanent-state')[0].value;
            district_name = e.target.value;
            $.ajax({
                method: "POST",
                url: "/api/vd/cities",
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify({'state': state_name, 'district': district_name})
            }).then(data => {
                console.log(data);
                //Populate the district drop down
                var option = '';
                var stateLen = data.cities.length;
                console.log(stateLen);
                $('#id_permanent-subdistrict').empty();
                $('#id_permanent-village').empty();
                for (var i = 0; i < stateLen; i++) {
                    console.log(data.cities[i])
                    option = '<option value="' + data.cities[i] + '">' + data.cities[i] + '</option>';
                    $('#id_permanent-subdistrict').append(option);

                }
            })
        }
    );
    $('#id_permanent-subdistrict').on('change', (e) => {
            state_name = $('#id_permanent-state')[0].value;
            district_name = $('#id_permanent-district')[0].value;
            subdistrict_name = e.target.value;
            $.ajax({
                method: "POST",
                url: "/api/vd/villages",
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify({'state': state_name, 'district': district_name, 'subdistrict': subdistrict_name})
            }).then(data => {
                console.log(data);
                //Populate the district drop down
                var option = '';
                var stateLen = data.villages.length;
                console.log(stateLen);
                $('#id_permanent-village').empty();
                for (var i = 0; i < stateLen; i++) {
                    console.log(data.villages[i])
                    option = '<option value="' + data.villages[i] + '">' + data.villages[i] + '</option>';
                    $('#id_permanent-village').append(option);

                }
            })
        }
    );
})