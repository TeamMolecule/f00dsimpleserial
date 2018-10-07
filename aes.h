/* This AES-128 comes from https://github.com/kokke/tiny-AES128-C which is released into public domain */

#ifndef _AES_H_
#define _AES_H_

#include "types.h"

#ifndef AES_CONST_VAR
//#define AES_CONST_VAR static const
#define AES_CONST_VAR
#endif


void AES128_ECB_encrypt(u8_t* input, u8_t* key, u8_t *output);
void AES128_ECB_decrypt(u8_t* input, u8_t* key, u8_t *output);

void AES128_ECB_indp_setkey(u8_t* key);
void AES128_ECB_indp_crypto(u8_t* input);



#endif //_AES_H_